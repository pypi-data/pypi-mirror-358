<p align="center">
  <img width="200" src="https://raw.github.com/UnicornGlade/PolariniFocusini/master/docs/.images/polarini_focusini.jpg" alt="Polarini Focusini project logo">
</p>

# Polarini Focusini

Automated **in-focus region detector** that blends monocular depth estimation with classic frequency-domain (Difference of Gaussian - **DoG**) sharpness cues.

# Example

<p align="left">
  <img width="400" src="https://raw.github.com/UnicornGlade/PolariniFocusini/master/docs/.images/processing_sample.jpg" alt="Example how in-focus part of photo is detected">
</p>

# What happens under the hood

1. Runs **[Depth-Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)** to get floating-point depth.  
2. Builds a 3-level **Gaussian pyramid** and two **Difference-of-Gaussians (DoG)** maps.  
3. Applies **Non-Maximum Suppression** in space *and* across scales.  
4. Keeps only strong extrema → votes for focus → finds dominant depth bins.  
5. Saves every intermediate step to a per-image `debug/` folder for easy inspection.

# Live coding walkthrough 🎬

Watch the 90-minute live “vibe-coding” session that produced this repo (**English code** + **English subs** + Russian-language commentary):

<p align="left">
  <a href="https://www.youtube.com/playlist?list=PL5p-5hHpsHBovPGgF-U1XPFas_RFW4F8A"><img width="400" src="https://raw.github.com/UnicornGlade/PolariniFocusini/master/docs/.images/youtube_thumbnail.jpg" alt="Link to youtube live coding sessions playlist"></a>
</p>

# Please cite ⭐

```
@misc{poliarnyi2025,
  title        = {Polarini Focusini: open-source pipeline for in-focus region detection},
  howpublished = {\url{https://github.com/UnicornGlade/PolariniFocusini}},
  author       = {Poliarnyi, N.},
  year         = {2025},
  note         = {YouTube demo: “Finding Focus in Photos Using Depth Anything and DoG”}
}
```

# Stars, forks, issues – all very welcome!
