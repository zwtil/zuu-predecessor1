this project is archived in favor of https://github.com/ZackaryW/zuu (better name, better structure)

[![Upload Python Package](https://github.com/ZackaryW/zrcl2/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ZackaryW/zrcl2/actions/workflows/python-publish.yml)

# zrcl
zack's reusable common library

* a library that contains reusable utilities to make my life easier
* 2 is only the repo-serial, I will still use `zrcl` as the package name
* package does not install any dependencies by default, it is up to the user to install them
* all functions are properly type hinted and docstringed

## Install
stable
```bash
pip install zrcl
```

or
```bash
pip install git+https://github.com/ZackaryW/zrcl2.git
```

beta
> branch using beta
```bash
pip install git+https://github.com/ZackaryW/zrcl2.git@beta
```

## Project Structure
* `beta_` means this is not finalized and not properly tested
* `ext_` means this is an extension to the original package (util functions for qol)
* `tool_` means this is an executable tool
* `app_` means this contains utils for an app (by default assume Windows is the sole working platform)
if exclusively specified as `app_win_` or `app_linux_` or `app_mac_` then it is for the respective platform

## Additional
* `zrcl` command is available and can be used to pass command and parameters for other tools

