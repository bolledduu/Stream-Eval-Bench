"""Reuse deterministic per-image encoder outputs; this is compute reuse, not a method."""
import hashlib,json,pathlib,time

def install(model,root):
    import torch
    original=model.visual.forward
    cache=pathlib.Path(root)/'vision_features';cache.mkdir(exist_ok=True)
    def feature(pixel_values,grid_thw):
        key=hashlib.sha256(pixel_values.contiguous().view(torch.uint8).numpy().tobytes()+grid_thw.contiguous().numpy().tobytes()).hexdigest()
        path=cache/(key+'.pt')
        if path.exists():return torch.load(path,map_location='cpu',weights_only=True)
        start=time.perf_counter()
        result=original(pixel_values,grid_thw=grid_thw).detach()
        torch.save(result,path)
        print('Encoded image',key[:12],'seconds',round(time.perf_counter()-start,2),flush=True)
        return result
    def cached(pixel_values,grid_thw):
        outputs=[];start=0
        for grid in grid_thw:
            size=int(grid.prod().item())
            outputs.append(feature(pixel_values[start:start+size],grid.unsqueeze(0)))
            start+=size
        assert start==pixel_values.shape[0]
        return torch.cat(outputs,dim=0)
    # Small engineering check: block-diagonal image attention must preserve per-image outputs.
    # Synthetic tensors here are only an implementation test, never benchmark data.
    grid=torch.tensor([[1,2,2],[1,2,2]],dtype=torch.long)
    patch_dim=model.config.vision_config.in_channels*model.config.vision_config.temporal_patch_size*model.config.vision_config.patch_size**2
    test=torch.zeros((8,patch_dim),dtype=model.visual.get_dtype());test[4:]=.25
    with torch.inference_mode():
        batch=original(test,grid_thw=grid)
        separate=torch.cat([original(test[:4],grid_thw=grid[:1]),original(test[4:],grid_thw=grid[1:])],dim=0)
    difference=float((batch-separate).abs().max())
    torch.testing.assert_close(batch,separate,rtol=.02,atol=.02)
    (pathlib.Path(root)/'results/cache_check.json').write_text(json.dumps({'passed':True,'max_absolute_difference':difference,'scope':'small synthetic engineering check, not research evidence','cache':'per-image encoder only; language decoding remains conditioned on the complete prompt'},indent=2))
    model.visual.forward=cached
