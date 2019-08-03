# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

# [1.2.1] - 2019-8-3
### Fixed
 - App can accept image files with capitalized extensions (e.g. ".JPG"").
### Added
 - Basic tests

# [1.2.0] - 2019-7-28
### Changed
 - Prediction service app is available on Dockerhub.
 - Prediction service no longer uses `nginx`.

# [1.1.0] - 2019-6-1
### Added
 - 2012-2014 and 2018 Lincoln Park Zoo datasets

# [1.0.4] - 2019-6-3
### Fixed
 - Travis badge URLs after repo moved
### Added
 - Sample images in README

# [1.0.3] - 2019-5-31
### Added
 - CODEOWNERS file

# [1.0.2] - 2019-5-30
### Added
 - More description of project in README.

# [1.0.1] - 2019-5-25
### Added
 - PR template
### Changed
 - Code is PEP8-compliant.

# [1.0.0] - 2019-4-13
### Changed
 - Rewrote dataset building code, offloading a lot of complexity to Creevey.
 - Rewrote model training code, using fast.ai library in a notebook rather than Tensorflow script.
 - Revised model serving code to use fast.ai model.

# [0.2.0] - 2019-2-24
### Changed
 - Reorganized repo, started CHANGELOG
