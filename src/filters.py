import numpy as np

from PIL import Image

def gabor_filter(im, orientim, freqim, mask, blocksize = 11):
    # Return a gabor filtered image

    filtered_im = np.zeros(im.shape)
    blockhalf = int(blocksize / 2)

    rows, cols = im.shape
    for r in range(blockhalf, rows-blockhalf):
        for c in range(blockhalf, cols-blockhalf):
            if mask[r,c] == False:
                continue
            o = orientim[r,c]
            f = freqim[r,c]
        
            filtered_im[r,c] = np.sum( np.rot90(h(blocksize, o, f)) * im[r-blockhalf:r+blockhalf+1,c-blockhalf:c+blockhalf+1] )

    filtered_im = np.where(filtered_im > 0, True, False) # binarize
    Image.fromarray(filtered_im).show()
    return filtered_im

def h(blocksize, phi, f):
    conv_mat = [] # Will hold the resulting convolution matrix
    u_phi_list = [] # Holds the u_phi values to be later used as the cosine argument

    halfblock = int(blocksize/2)

    delta_u_sq = delta_v_sq = 16 # the squared deltas, as they don't change during the filter generation
    for v in range(-halfblock, halfblock + 1):
        # pre-compute the second part of u_phi and v_phi
        pre_u_phi = v * np.sin(phi)
        pre_v_phi = v * np.cos(phi)
        for u in range(-halfblock, halfblock + 1):
            u_phi = u * np.cos(phi) + pre_u_phi
            v_phi = -u * np.sin(phi) + pre_v_phi

            exp_arg = ( -1/2 * ((u_phi**2 / delta_u_sq) + (v_phi**2 / delta_v_sq)) )

            u_phi_list.append(u_phi)
            conv_mat.append(exp_arg)

    u_phi_list = np.array(u_phi_list).reshape((blocksize, blocksize))
    conv_mat = np.array(conv_mat).reshape((blocksize, blocksize))

    cos_args = np.cos(2* np.pi * f * u_phi_list) # compute the cosine part of the gabor filter matrix
    conv_mat = np.exp(conv_mat) * cos_args # compute the gabor filter matrix

    return conv_mat