import numpy as N
import modred as MR
from custom_vector import CustomVector, CustomVecHandle, inner_product

parallel = MR.parallel.default_instance

# define snapshots to use
direct_snapshots = [CustomVecHandle('direct_snap%d.pkl'%i,
    scale=N.pi) for i in range(10)]
adjoint_snapshots = [CustomVecHandle('adjoint_snap%d.pkl'%i,
    scale=N.pi) for i in range(10)]
    
# generate fake random data (for example purposes only)
nx = 50
ny = 30
nz = 20
x = N.linspace(0, 1, nx)
y = N.logspace(1, 2, ny)
z = N.linspace(0, 1, nz)**2
if parallel.is_rank_zero():
    for snap in direct_snapshots + adjoint_snapshots:
        snap.put(CustomVector([x, y, z], 
                              N.random.random((nx, ny, nz))))
parallel.barrier()

# compute balanced POD
bpod = MR.BPOD(inner_product=inner_product)
bpod.sanity_check(direct_snapshots[0])
L_sing_vecs, sing_vals, R_sing_vecs = \
    bpod.compute_decomp(direct_snapshots, adjoint_snapshots)

# Model error less than ~10%
sing_vals_norm = sing_vals / N.sum(sing_vals)
num_modes = N.nonzero(N.cumsum(sing_vals_norm) > 0.9)[0][0] + 1
mode_nums = range(num_modes)

direct_modes = [CustomVecHandle('direct_mode%d.pkl'%i) 
                for i in mode_nums] 
adjoint_modes = [CustomVecHandle('adjoint_mode%d.pkl'%i) 
                 for i in mode_nums]

bpod.compute_direct_modes(mode_nums, direct_modes)
bpod.compute_adjoint_modes(mode_nums, adjoint_modes)
