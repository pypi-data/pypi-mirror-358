# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
* Added ruff as additional formatter
* Overwriting the initialize_model method in case defined

### Changes
* Improved error handling and logging by adding try-except blocks and debug logging of tracebacks in various model logging modules.
* Simplified the code_dir functionality by skipping the processing step before zipping directories
* Adapting logging for the `JmlCustomerClient`
* Removing the restriction of being a JFML customer for logging a model version

### Fixes

### Breaks


## 0.0.13 - (2025-05-13)
---

### Changes
* Updating `frogml-core` dependency


## 0.0.12 - (2025-03-18)
---

### New
* Supporting custom code to be uploaded along a model version


### Breaks
* If uploaded, custom code must contain a file that inherits from `frogml.FrogMlModel`


## 0.0.11 - (2025-03-16)


## 0.0.10 - (2025-03-02)

### Changes
* Adding dev dependency publish when published to main
* Using uv instead of poetry

## 0.0.9 - (2025-02-27)

### Changes
* Removing `scikit-learn` dependencies for non-`scikit-learn` extra packages


## 0.0.8 - (2025-02-24)

### Changes
* upgrading frogml-core and frogml-storage packages

### Fixes
* default model version not set


## 0.0.7 - (2025-02-23)

## 0.0.6 - (2025-02-20)

### Changes
* log_model also records the framework version used


## 0.0.5 - (2025-02-18)

## 0.0.4 - (2025-02-16)

## 0.0.3 - (2025-02-16)

### Breaks
* Removed support for the namespace argument


## 0.0.2 - (2025-02-05)

## 0.0.1 - (2024-12-04)

### New
* Starting Frog Ml Sdk project
