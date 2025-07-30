import math
import torch
import torch.nn.functional as F
from torch.nn.utils import spectral_norm
from torch import nn
from torch.utils.checkpoint import checkpoint
from torchmetrics.image.fid import FrechetInceptionDistance
from torchvision.ops import sigmoid_focal_loss


from .patch_discriminator import PatchDiscriminator
from .vqgan_plus import VQGANPlusPatchDiscriminator
from .general import ldcfg, print_vram

### Related to losses/differentiable metrics
# Note: not all of these actually get used all the time... 


from geomloss import SamplesLoss


def sinkhorn_loss_chunked(target, gen, chunk_size=256, device='cuda'):
    """Chunked sinkhorn to reduce memory usage"""
    assert target.shape == gen.shape, f"target.shape {target.shape} != gen.shape {gen.shape}"
    sinkhorn_fn = SamplesLoss(loss="sinkhorn", p=2, blur=0.05)

    total_loss, num_chunks = 0.0, 0
    for i in range(0, target.shape[0], chunk_size):
        end_idx = min(i + chunk_size, target.shape[0])
        target_chunk = target[i:end_idx].reshape(end_idx - i, -1).to(device)
        gen_chunk = gen[i:end_idx].reshape(end_idx - i, -1).to(device)

        chunk_loss = sinkhorn_fn(target_chunk, gen_chunk).item()
        total_loss += chunk_loss
        num_chunks += 1

        del target_chunk, gen_chunk
        torch.cuda.empty_cache()

    return total_loss / num_chunks

def sinkhorn_loss(target, gen, max_B=None, device='cuda', chunk=False, debug=False):
    if chunk: return sinkhorn_loss_chunked(target, gen, device=device)

    sinkhorn_fn = SamplesLoss(loss="sinkhorn", p=2, blur=0.05)
    # usage: metrics['sinkhorn'] = sinkhorn_loss(target, integrator_outputs)
    # max_B limits eval batch size bc Sinkhorn calc can be slow, max_B=None means use whole batch
    assert target.shape == gen.shape, f"target.shape {target.shape} != gen.shape {gen.shape}"
    B = target.shape[0] if max_B is None else min(target.shape[0], max_B) 
    t_vec, g_vec = [x[:B].reshape(B, -1).to(device) for x in (target, gen)]

    if debug: # : check value ranges
        print(f"sinkorn_loss: Target:    mean={t_vec.mean():.3f}, std={t_vec.std():.3f}, range=[{t_vec.min():.3f}, {t_vec.max():.3f}]")
        print(f"sinkorn_loss: Generated: mean={g_vec.mean():.3f}, std={g_vec.std():.3f}, range=[{g_vec.min():.3f}, {g_vec.max():.3f}]")
  
    return sinkhorn_fn(t_vec, g_vec).item()


def focal_loss(pred,                    # pred: logits tensor
              target_binary,           # target_binary: binary tensor
              alpha=0.9,              # class weighting: higher values give more weight to positive class
              gamma=2.0):              # focusing parameter: higher values focus more on hard examples
   """Focal loss for binary classification with logits, handles imbalanced loads"""
   return sigmoid_focal_loss(pred, target_binary, alpha=alpha, gamma=gamma, reduction='mean')
   #bce = F.binary_cross_entropy_with_logits(pred, target_binary, reduction='none')
   #p_t = torch.exp(-bce)  # probability of correct class
   #alpha_t = alpha * target_binary + (1 - alpha) * (1 - target_binary)  # class weighting
   #focal_weight = alpha_t * (1 - p_t) ** gamma
   #return (focal_weight * bce).mean()


def piano_roll_rgb_cross_entropy(pred,                  # pred: [B, C, H, W] tensor of predicted probabilities 
                                 target,                # target: [B, C, H, W] tensor of ground truth RGB where:
                                                            # - black = [0,0,0] (background)
                                                            # - red = [1,0,0] (onset)
                                                            # - green = [0,1,0] (sustain)
                                 temperature=0.25,      # Temperature for softening predictions (higher = softer)
                                 onset_threshold=0.3,   # Value above which a color of onset channel is considered "on"
                                 sustain_threshold=0.5, # Value above which a color of sustain channel is considered "on"
                                 eps=1e-8,              # Small value to avoid log(0)
                                 debug=False):
    """    Compute cross entropy loss for RGB piano roll images with thresholding    """
    if debug: 
        print(f"pred.shape = {pred.shape}, target.shape = {target.shape}")
        print(f"pred.min(),   pred.max() = ",pred.min(), pred.max())
        print(f"target.min(), target.max() = ",target.min(), target.max())
    #targets & preds may have imagenet norm (if dataloader norm'd them) so before doing BCE loss we need to un-norm them
    target_unnorm = target  #...? did i forget to do something here?
    
    thresholds = torch.tensor([onset_threshold, sustain_threshold, 1.0])[None,:,None,None].to(target.device)

    if target.shape[1] == 1:  # Grayscale case
        thresholds = torch.tensor([sustain_threshold])[None,:,None,None].to(target.device)
    else:  # RGB case: Different thresholds for each color (background, onset, sustain) channel
        thresholds = torch.tensor([onset_threshold, sustain_threshold, 1.0])[None,:,None,None].to(target.device)

    target_binary = torch.where(target_unnorm > thresholds, torch.ones_like(target), torch.zeros_like(target))
    pred = pred / temperature # Scale logits by temperature
    if debug: print(f"pred.shape = {pred.shape}, target_binary.shape = {target_binary.shape}")
    #loss = F.binary_cross_entropy_with_logits(pred, target_binary)
    loss = focal_loss(pred, target_binary)
    return loss.mean() # Sum across channels and average over batch and spatial dimensions



def perceptual_loss(vgg, img1, img2):
    # Normalize images to VGG range
    mean = torch.tensor([0.485, 0.456, 0.406])[None, :, None, None].to(img1.device)
    std = torch.tensor([0.229, 0.224, 0.225])[None, :, None, None].to(img1.device)
    img1, img2 = (img1 - mean) / std, (img2 - mean) / std

    features1, features2 = vgg(img1), vgg(img2) # Get features from multiple layers
    
    # Compute loss at each layer
    loss = 0
    for f1, f2 in zip(features1, features2):
        loss += F.mse_loss(f1, f2)
    return loss


# In metrics.py, replace perceptual_loss function:
def resnet_perceptual_loss(img1, img2, device='cuda'):
    """ResNet50 logits-based perceptual loss as used in VQGAN+;  Not good for MIDI"""
    import torchvision.models as models

    # Load pretrained ResNet50 (cache this globally)
    if not hasattr(resnet_perceptual_loss, 'resnet'):
        resnet_perceptual_loss.resnet = models.resnet50(pretrained=True).to(device).eval()
        for param in resnet_perceptual_loss.resnet.parameters():
            param.requires_grad = False

    resnet = resnet_perceptual_loss.resnet

    # Normalize to ImageNet range
    mean = torch.tensor([0.485, 0.456, 0.406])[None, :, None, None].to(device)
    std = torch.tensor([0.229, 0.224, 0.225])[None, :, None, None].to(device)

    img1_norm = (img1 - mean) / std
    img2_norm = (img2 - mean) / std

    # Get logits (before final classification layer)
    logits1 = resnet(img1_norm)
    logits2 = resnet(img2_norm)

    return F.mse_loss(logits1, logits2)


def pwrspec(y, eps=1e-4): 
    # called by spectral_loss; 
    # Note: to avoid gradient explosion, don't use the log of this with autograd. Though log(1 + this) is maybe ok 
    if y.dtype != torch.float: 
        y = y.to(torch.float)  # Cast to float even if MP's on, b/c fft isn't optimized for half
    return torch.abs(torch.fft.fft2(y)) # just the magnitude, no phase info. 

def spectral_loss(x, x_recon):
    """optional: experimental and not needed"""
    x_spec, x_recon_spec = pwrspec(x), pwrspec(x_recon)
    # TODO: maybe flatten the spectrum or just grab high freqs; spatial MSE loss (elsewhere) already emphasizes the lows
    if torch.is_autocast_enabled(): 
        x_spec = x_spec.to(torch.half)
        x_recon_spec = x_recon_spec.to(torch.half) 
    return F.mse_loss(x_spec, x_recon_spec)



def compute_vqgan_losses(recon, target_imgs, vq_loss, vgg, adv_loss=None, epoch=None, config=None, fakez_recon=None): #,sinkhorn_loss=None,)
    """Compute many losses in a single place. Returns dict of loss tensors."""
    # Check inputs for NaN
    if torch.isnan(vq_loss).any():
        print(f"vq_loss is NaN at START of compute_vqgan_losses")


    losses = {
        'mse': F.mse_loss(recon, target_imgs),
        'vq': vq_loss, # vq_loss is already computed in the quantizer (bottleneck of the VQGAN) 
    }
    cc = config.codec 
    if cc.lambda_perc > 0: 
        losses['perceptual'] = perceptual_loss(vgg, recon, target_imgs)
    #'perceptual': resnet_perceptual_loss(recon, target_imgs),  # as per VQGAN+
    #'spectral': spectral_loss(recon, target_imgs),  # nah
    # 'huber': F.huber_loss(recon, target_imgs, delta=1.0) 

    if cc.lambda_ce > 0: # anything where we demand pixel-wise presision, e.g. MIDI
        losses['ce'] =  piano_roll_rgb_cross_entropy(recon, target_imgs)
    
    # Only add adversarial losses after warmup
    if adv_loss is not None and epoch >= config.codec.warmup_epochs:
        d_loss, real_features = adv_loss.discriminator_loss(target_imgs, recon)
        g_loss = adv_loss.generator_loss(recon, real_features)
        losses['d_loss'] = d_loss
        losses['g_loss'] = config.codec.lambda_gen * g_loss

    for k, v in losses.items():  # not enumerate
        if torch.isnan(v).any() or torch.isinf(v).any():
            print(f"compute_vqgan_losses: Bad loss values for {k}: nan={torch.isnan(v).sum()}, inf={torch.isinf(v).sum()}")

    return losses


def get_total_vqgan_loss(losses, config):
    """Compute weighted sum of losses."""
    cc = config.codec
    total = (cc.lambda_mse * losses.get('mse', 0.0) +
             cc.lambda_vq * losses.get('vq', 0.0) +
             cc.lambda_ce * losses.get('ce', 0.0) +
             cc.lambda_perc * losses.get('perceptual', 0.0) +
             losses.get('g_loss', 0.0)  )
             # other losses I tried but don't need: 
             # + cc.lambda_spec * losses['spectral'] \
             #+ cc.lambda_l1*losses['huber'] + \
             #+ cc.lambda_sinkhorn * losses.get('s_loss', 0.0))
    return total


#------------------------------------------------------------------
# Next section used in training VQGAN. Besides oridnary reconstruction loss, we include a Patch-based discriminator model

def hinge_d_loss(real_pred, fake_pred):
    return torch.mean(F.relu(1.0 - real_pred)) + torch.mean(F.relu(1.0 + fake_pred))


class AdversarialLoss(nn.Module):
    def __init__(self, device, in_channels=3, use_checkpoint=False):
        super().__init__()

        self.device = device
        #self.discriminator = PatchDiscriminator(in_channels=in_channels, use_checkpoint=use_checkpoint).to(device)
        self.discriminator = VQGANPlusPatchDiscriminator(in_channels=in_channels, use_checkpoint=use_checkpoint).to(device)
        self.criterion = hinge_d_loss

        self.register_buffer('real_label', torch.ones(1))
        self.register_buffer('fake_label', torch.zeros(1))
        self.to(device)


    def get_target_tensor(self, prediction, target_is_real):
        target = self.real_label if target_is_real else self.fake_label
        return target.expand_as(prediction)

    def feature_matching_loss(self, real_features, fake_features):
        loss = 0
        for real_feat, fake_feat in zip(real_features, fake_features):
            loss += F.l1_loss(fake_feat, real_feat.detach())
        return loss / len(real_features)

    def discriminator_loss(self, real_images, fake_images):
        real_pred, real_features = self.discriminator(real_images)
        fake_pred, _ = self.discriminator(fake_images.detach())
        return hinge_d_loss(real_pred, fake_pred), real_features

    def generator_loss(self, fake_images, real_features=None):
        fake_pred, fake_features = self.discriminator(fake_images)
        g_loss = -torch.mean(fake_pred)
        if real_features is not None:
            fm_loss = self.feature_matching_loss(real_features, fake_features)
            g_loss = g_loss + fm_loss
        return g_loss
#-------- end adversarial part---------------------------------------------
    


### End differentiable metric stuff

#### Non-differentiable metrics --- 

def to_uint8(x):
    # used by fid_score calculators, below
    x = x.clone().detach()  # Ensure no gradients
    x -= x.amin(dim=(1,2,3), keepdim=True)
    x /= x.amax(dim=(1,2,3), keepdim=True).clamp(min=1e-5)
    return (x * 255).clamp(0, 255).to(torch.uint8)

@torch.no_grad()
def fid_score_chunked(real, fake, chunk_size=256, device='cuda'):
    """FID with chunked processing"""
    fid_calculator = FrechetInceptionDistance(feature=2048).to(device)
    fid_calculator.reset()

    # Process in chunks
    for i in range(0, real.shape[0], chunk_size):
        end_idx = min(i + chunk_size, real.shape[0])
        real_chunk = to_uint8(real[i:end_idx])
        fake_chunk = to_uint8(fake[i:end_idx])

        if real_chunk.shape[1] == 1:
            real_chunk = real_chunk.repeat(1, 3, 1, 1)
            fake_chunk = fake_chunk.repeat(1, 3, 1, 1)

        fid_calculator.update(real_chunk, real=True)
        fid_calculator.update(fake_chunk, real=False)

        # Clear chunk memory
        del real_chunk, fake_chunk
        torch.cuda.empty_cache()

    return fid_calculator.compute().item()


@torch.no_grad()
def fid_score(real, fake, device='cuda', chunk=False):
    if chunk: return fid_score_chunked(real, fake, device=device)

    fid_calculator = FrechetInceptionDistance(feature=2048)  
    fid_metric, real, fake = fid_calculator.to(device), real.to(device), fake.to(device)

    real_uint8 = to_uint8(real)
    fake_uint8 = to_uint8(fake)

    if real_uint8.shape[1] == 1: 
        real_uint8 = real_uint8.repeat(1, 3, 1, 1)
        fake_uint8 = fake_uint8.repeat(1, 3, 1, 1)

    fid_metric.reset()
    fid_metric.update(real_uint8, real=True)
    fid_metric.update(fake_uint8, real=False)
    return fid_metric.compute().item()


# TODO: some of these are already defined elsewhere; import
def rgb2g(img_t):
   """Convert RGB piano roll to grayscale float where: BLACK->0, RED->1.0, GREEN->0.5
   Changes image from [3,H,W] to [1,H,W], and can include batch dimension."""
   red = (img_t[-3] > 0.5).float()  # 1.0 for red
   green = (img_t[-2] > 0.5).float() * 0.5  # 0.5 for green
   return (red + green).unsqueeze(-3)

def g2rgb(gf_img, keep_gray=False): # gf = greyscale floatw
   """Convert grayscale back to RGB and quantizes
   0->BLACK, 1.0->RED, 0.5->GREEN, unless keep_gray is on in which case it becomes binary rgb black/while"""
   if gf_img.shape[-3] == 3: return gf_img
   gf = gf_img.squeeze(-3)
   if keep_gray: 
        binary_img = (gf > 0.5).float()  # or whatever threshold
        return binary_img.unsqueeze(-3).repeat(1, 3, 1, 1)
   return torch.stack([(gf >= 0.75).float(), (torch.abs(gf - 0.5) < 0.25).float(), torch.zeros_like(gf)], dim=-3)


def targ_pred_mask_to_rgb(t_mask, p_mask):
    # put t_mask on red channel, and p_mask on gren channel and leave blue as zero
    rgb_tensor = torch.cat([t_mask.unsqueeze(0), p_mask.unsqueeze(0), torch.zeros_like(t_mask).unsqueeze(0)], dim=0)
    #rgb_tensor = torch.cat([t_mask, p_mask, torch.zeros_like(t_mask)], dim=1)
    return rgb_tensor

def mask_to_rgb(mask, color=[1,1,1]):  # default white
    rgb = torch.zeros((mask.shape[0], 3, mask.shape[1], mask.shape[2]), device=mask.device)
    for i in range(3):
        rgb[:,i,:,:] = mask * color[i]
    return rgb

def analyze_positions(p_mask, t_mask, limit=10):
    # Get indices of positive pixels
    p_pos = torch.nonzero(p_mask, as_tuple=True)  # Get separate tensors for each dimension
    t_pos = torch.nonzero(t_mask, as_tuple=True)

    print(f"\nShape of prediction mask: {p_mask.shape}")
    print(f"Shape of target mask: {t_mask.shape}")

    print(f"\nFirst {limit} prediction positions:")
    # Print full coordinate tuples for each position
    for i in range(min(limit, len(p_pos[0]))):
        pos = tuple(dim[i].item() for dim in p_pos)
        print(f"   {pos}")

    print(f"\nFirst {limit} target positions:")
    for i in range(min(limit, len(t_pos[0]))):
        pos = tuple(dim[i].item() for dim in t_pos)
        print(f"   {pos}")


def calc_note_metrics(pred, target, threshold=0.4, minval=None, maxval=None, keep_gray=False, debug=False):
    if debug: print(f"calc_note_metrics: Before:  pred.shape = {pred.shape}, target.shape = {target.shape}")
    pred, target = g2rgb(pred, keep_gray=keep_gray), g2rgb(target, keep_gray=keep_gray)
    if debug: print(f"calc_note_metrics: After:  pred.shape = {pred.shape}, target.shape = {target.shape}")
    if minval is None:  minval = target.min()
    if maxval is None:  maxval = target.max()
    pred_clamped = torch.clamp(pred.clone(), minval, maxval)
    target_unit = (target - minval) / (maxval - minval)  # rescale to [0,1]
    pred_unit = (pred_clamped - minval) / (maxval - minval)

       
    pred_binary = torch.where(pred_unit > threshold, torch.ones_like(pred_unit), torch.zeros_like(pred_unit))
    target_binary = torch.where(target_unit > threshold, torch.ones_like(target_unit), torch.zeros_like(target_unit))
    metrics, metric_images = {}, {}

    # print a range of values to check for alignment issues
    b, i_start, j_start, square_size = 1, 50, 50, 6
    c = 1 # channel
    if debug:
        print("target_unit[square] = \n", target_unit[b,c,i_start:i_start+square_size, j_start:j_start+square_size].cpu().numpy())
        print("pred_unit[square] = \n",     pred_unit[b,c,i_start:i_start+square_size, j_start:j_start+square_size].cpu().numpy())
        print("target_binary[square] = \n", target_binary[b,c,i_start:i_start+square_size, j_start:j_start+square_size].cpu().numpy())
        print("pred_binary[square] = \n",     pred_binary[b,c,i_start:i_start+square_size, j_start:j_start+square_size].cpu().numpy())
    
    # separate masks for onset and sustain
    for i, name in enumerate(['onset', 'sustain']):
        channel = 0 if i == 0 else 1  # Red=onset, Green=sustain
        
        # Initialize total counters
        total_tp = 0
        total_tn = 0
        total_fp = 0
        total_fn = 0
        
        # Initialize aggregated metric images
        tp_img = torch.zeros_like(pred_binary[:,0])
        tn_img = torch.zeros_like(pred_binary[:,0])
        fp_img = torch.zeros_like(pred_binary[:,0])
        fn_img = torch.zeros_like(pred_binary[:,0])
        targpred_img = torch.zeros_like(target)
        
        # Process each batch item separately
        for b in range(pred_binary.shape[0]):
            p_mask = pred_binary[b, channel]
            t_mask = target_binary[b, channel]
            
            # Calculate metrics for this batch item
            tp_batch = (p_mask == 1) & (t_mask == 1)
            tn_batch = (p_mask == 0) & (t_mask == 0)
            fp_batch = (p_mask == 1) & (t_mask == 0)
            fn_batch = (p_mask == 0) & (t_mask == 1)
            
            # Add to totals
            total_tp += torch.sum(tp_batch).float()
            total_tn += torch.sum(tn_batch).float()
            total_fp += torch.sum(fp_batch).float()
            total_fn += torch.sum(fn_batch).float()
            
            # Add to metric images
            tp_img[b] = tp_batch.float()
            tn_img[b] = tn_batch.float()
            fp_img[b] = fp_batch.float()
            fn_img[b] = fn_batch.float()
            targpred_img[b] = targ_pred_mask_to_rgb(t_mask, p_mask)
        
        if debug:
            print(f"Channel: {channel}")
            print(f"   Number of 1s in p_mask: {torch.sum(pred_binary[:,channel] == 1)}")
            print(f"   Number of 1s in t_mask: {torch.sum(target_binary[:,channel] == 1)}")
            print(f"   Number of positions where both are 1: {total_tp}")
            
        metrics.update({
            f'{name}_sensitivity': (total_tp / (total_tp + total_fn + 1e-8)).item(), # aka recall
            f'{name}_specificity': (total_tn / (total_tn + total_fp + 1e-8)).item(),
            f'{name}_precision': (total_tp / (total_tp + total_fp + 1e-8)).item(),
            f'{name}_f1': (2 * total_tp / (2 * total_tp + total_fp + total_fn + 1e-8)).item()
        })
        
        # Convert binary masks to RGB for visualization
        def mask_to_rgb(mask):
            return mask.unsqueeze(1).repeat(1, 3, 1, 1)
            
        metric_images.update({
            f'{name}_tp': mask_to_rgb(tp_img),
            f'{name}_tn': mask_to_rgb(tn_img), 
            f'{name}_fp': mask_to_rgb(fp_img),
            f'{name}_fn': mask_to_rgb(fn_img),
            f'{name}_targpred': targpred_img,
        })
        
        if debug:
            print(f" {name}: tp, tn, fp, fn =", [int(x.item()) for x in [total_tp, total_tn, total_fp, total_fn]])
            
    return metrics, metric_images




def get_discriminator_stats(adv_loss, real_images, fake_images):
    with torch.no_grad():
        d_real = adv_loss.discriminator(real_images)[0].mean()  # Add [0] to get first element of tuple
        d_fake = adv_loss.discriminator(fake_images)[0].mean()  # Add [0] to get first element of tuple
        return {
            'd_real_mean': d_real.item(),
            'd_fake_mean': d_fake.item(),
            'd_conf_gap': (d_real - d_fake).item()
        }

def get_gradient_stats(discriminator):
    total_norm = 0.0
    for p in discriminator.parameters():
        if p.grad is not None:
            total_norm += p.grad.data.norm(2).item() ** 2
    return {'d_grad_norm': math.sqrt(total_norm)}




@torch.no_grad()
# general utility called in evaluate_model 
def compute_sample_metrics(pred_latents, target_latents,   # latent space
                           decoded_pred, decoded_target,   # pixel space
                           debug=False):
    """Compute metrics between predicted and target samples"""
    batch_size = min(pred_latents.shape[0], target_latents.shape[0])
    if debug: print("compute_sample_metrics: using batch_size = ",batch_size)
    if debug: print_vram("start")

    with torch.no_grad():
        if debug: print_vram("before sinkhorn_latent")
        sinkhorn_latent = sinkhorn_loss(target_latents[:batch_size], pred_latents[:batch_size])
        if debug: print_vram("after sinkhorn_latent, before sinkhorn_px")
        sinkhorn_px = sinkhorn_loss(decoded_target, decoded_pred)  # pixel space
        if debug: print_vram("after sinkhorn_px, before fid_px")
    fid_px = fid_score(decoded_target, decoded_pred)  # pixel space
    if debug: print_vram("after fid_px")

    metrics = { 
            'FID_px': fid_px, 
            'sinkhorn': sinkhorn_latent, 
            'sinkhorn_px': sinkhorn_px,
            # the following mse's won't be very meaningful for a generative model, but if we're learning inpainting,... maybe
            'mse': torch.nn.functional.mse_loss(pred_latents[:batch_size], target_latents[:batch_size]).item(),
            'mse_px': torch.nn.functional.mse_loss(decoded_pred, decoded_target).item(),
            'pred_mean': pred_latents.mean().item(),
            'targ_mean': target_latents.mean().item(),
            'pred_std': pred_latents.std().item(),
            'targ_std': target_latents.std().item(),
            'pred_px_mean': decoded_pred.mean().item(),
            'targ_px_mean': decoded_target.mean().item(), 
            'pred_px_std': decoded_pred.std().item(),
            'targ_px_std': decoded_target.std().item(),
        }

    # Cleanup
    del pred_latents, target_latents, decoded_pred, decoded_target
    if torch.cuda.is_available(): torch.cuda.empty_cache()

    if debug: print("metrics =",metrics)
    return metrics


