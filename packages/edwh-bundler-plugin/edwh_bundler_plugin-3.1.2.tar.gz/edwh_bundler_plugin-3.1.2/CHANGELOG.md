# Changelog

<!--next-version-placeholder-->

## v3.1.2 (2025-06-26)

### Fix

* Bump `sassquatch` version for proper macos support ([`5494773`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/5494773a3932090ba68c184a2a2bf16d0a7dc2cb))

## v3.1.1 (2025-05-22)

### Fix

* Better errors ([#3](https://github.com/educationwarehouse/edwh-bundler-plugin/issues/3)) ([`ebffc54`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/ebffc547eccf4cca837cb4273f1b64fbdd977c7d))

## v3.0.1 (2025-05-19)

### Fix

* Bump to sassquatch 1.0+ ([`4393820`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/4393820b0dacb90efa909d742a39e0ccdeb4f026))

### Documentation

* Replace libsass->dart-sass via sassquatch ([`0f84e48`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/0f84e4860fd3e922410f7b033addade2b3468d6e))

## v3.0.0 (2025-05-19)

### Feature

* Use sassquatch (based on dart-sass) instead of libsass so we can use `@use` ([`709304c`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/709304ccf54d21ad4904dfa88cd0729b71882e2c))

## v2.1.4 (2025-04-04)

### Fix

* **scss:** Also hide SSL certificate warnings ([`497a56d`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/497a56dc8e46c9ef1d8128d53ebdd40ed07d77c2))

## v2.1.3 (2025-03-27)

### Fix

* Don't check ssl when doing requests, (don't crash just warn) pt2 ([`835aea2`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/835aea2f5db47e8e24667f66df33ce1b93f1376d))

## v2.1.2 (2025-03-27)

### Fix

* Don't check ssl when doing requests, (don't crash just warn) ([`72fbf30`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/72fbf30f425f6253f17324c569a4a9cc032b66d6))

## v2.1.1 (2025-03-25)

### Fix

* Improved `.env` finding ([`f56d761`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/f56d7614c6c7bf6c82d5e6769b4d78e0c7576c11))

## v2.1.0 (2025-03-25)

### Feature

* Add `bundle.settings` to see the active settings for a specific config ([`571aa01`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/571aa019731284201b675766cdfc073f3115d4d1))

## v2.0.0 (2025-03-25)

### Feature

* **variables:** Also resolve $variables (local and .env) for other settings ([`8362a6b`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/8362a6b654efbb1a094073f7713df92e950a221d))

This may be a breaking change! While it probably won't disrupt most configurations, a major release is issued
conservatively.

## v1.3.0 (2024-11-29)

### Feature

* Improved `edwh publish`: ([`8365353`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/836535337a9f12596eb010e9829f35787bfc7646))

## v1.2.2 (2024-11-28)

### Fix

* Add gitignore in cdn_cache folder ([`8001e51`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/8001e5169cfb69524d3877333730e6828263d1ed))
* Raise exception if cdn returns an error status code instead of pasting the error text into the bundle ([`bb29424`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/bb294248ef421ca4553d80722e924536889432c9))


## v1.2.1 (2024-09-30)

### Fix

* Make `bundle.publish` work with multiple configurations ([`3376235`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/337623560cfa0620be60aa29e594327f7c00efb8))

## v1.2.0 (2024-09-30)

### Feature

* Allow specifying multiple `configurations`, include 'source' if output is not minified ([`ae2abf6`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/ae2abf6657633f3d54f2d5d5fb21362137ca3b6f))

## v1.1.0 (2024-07-04)

### Feature

* Started on TypeScript support via dukpy (+ custom loader for browser and buildtime import resolver) ([`a8ab5cd`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/a8ab5cda1030c16ac3e2faa67c5485e5a873dd80))

### Fix

* Minor tweaks in TS loading: ([`9366383`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/93663835cfd6fab2f17db4d66c3018c589288d3e))

### Documentation

* Added docstrings to new TS parts and updated README ([`ce0d8b2`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/ce0d8b24175b6607442cd2b79f2a10a75b270eb0))

## v1.0.6 (2024-04-22)

### Fix

* Also work with Path for should_publish ([`f58efe5`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/f58efe5dbf9057e68256af8e3621cd974d93e19b))

## v1.0.5 (2024-04-22)

### Fix

* Don't crash if 'setting' is not a str (e.g. Path) ([`9d817fe`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/9d817fe1ea04affd9e8d178fda5b50631a1b2a2c))

## v1.0.4 (2024-04-12)

### Fix

* Require_sudo before chmod ([`c50193a`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/c50193a8b5112e514a46b72d98cdaccedb1ad881))

## v1.0.3 (2024-02-02)
### Fix
* **pyproject:** Pyproject.toml can now be used via -c option (instead of as fallback only) ([`cfc0cf0`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/cfc0cf046409c63e74ae9394ccd5d8fc7f2c2f45))

## v1.0.2 (2024-01-16)
### Fix
* Database-based build now works via pathlib + auto creates tmp folders (incl. parents) ([`2eb06fa`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/2eb06fa4b74ca1cb67b816f33f6cbcc025877bcf))

## v1.0.1 (2024-01-16)
### Fix
* Better .toml loading + verbose logging ([`b01c6d7`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/b01c6d7733962a733d1217e5b0841a0d4b5ee87b))

### Documentation
* **config:** Explained more about the bundle.yaml file ([`f945ca4`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/f945ca478b8c1ebf22e656e398742835aab3ea10))

## v1.0.0 (2023-09-26)
### Feature
* Bundler can now load extra scss variables from yaml/toml/json/... ([`37e5707`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/37e57075d6c49168b759e292223abdae020145da))
* **scss:** WIP to load variables from file or url instead of yaml only ([`3d6ef99`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/3d6ef9904aa01a6110def2faf39e4260deed3aeb))
* **scss:** Scss variables can now be injected via Python ([`b73ebb0`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/b73ebb0d0b17bb3166e9cf41c2ee948008a175f0))

## v0.2.5 (2023-09-20)
### Fix
* Include the scss path so imports are resolved properly ([`427ff92`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/427ff92ae5479c5585733d05ec2acfa66f52a952))

## v0.2.4 (2023-09-20)
### Fix
* **sass:** Actually support sass next to scss ([`1e5cd99`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/1e5cd9985c8a9fee45bce46c64b1fa9b0b019c57))

## v0.2.3 (2023-09-20)
### Fix
* Inline multiline scss can now also be converted ([`964d28d`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/964d28d701782913be46b4f6b41b2a045873c99d))

### Documentation
* Copied README from previous repo ([`6464165`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/64641658cca6be8b957eb49afe706487a3a28ca0))

## v0.2.2 (2023-09-19)
### Performance
* **sass:** Re-introduced JIT imports to slightly speed up plugin ([`4433ae9`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/4433ae9cb3075e0ceb8b06ca7b09845b960aac89))

## v0.2.1 (2023-09-19)
### Performance
* **httpx:** Replaced httpx with requests because the import was very slow (150ms) ([`f51d1e9`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/f51d1e9dfe89bd6caa4ac782f09414d63beaa151))

## v0.2.0 (2023-07-11)
### Feature
* Support .toml and pyproject.toml with key tool.edwh.bundle ([`2ef6196`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/2ef6196264b7703cb73c28ce0bb56ce4bb498447))
* Allow `hash (bool)` option in config to store a .hash file of generated bundles ([`81d7720`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/81d7720ef6b50626542730ba511ecd3463e477ef))
* Made config a little more flexible by allowing '-' as well as '_' as a word seperator in keys ([`8a20fd8`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/8a20fd83e02e11153d36c623d8b214e0aa5f95b1))

## v0.1.7 (2023-06-29)
### Fix
* Don't crash if the output folder doesn't exist yet ([`630342d`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/630342dd149a0120cd003c6c09d7f1238797d3a5))

## v0.1.6 (2023-05-31)


## v0.1.5 (2023-04-17)


## v0.1.4 (2023-04-17)
### Fix
* **project:** Remove theoretical support for Python versions below 3.10 since that has never worked ([`daa3e39`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/daa3e39abe7627a09c93ccfeb42e164612c14b6c))

## v0.1.3 (2023-04-17)
### Fix
* **publish:** .db file moved to tmp ([`11613ca`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/11613caab17da02526358c5291a3f737c6d4b859))

## v0.1.2 (2023-04-11)
### Documentation
* **changelog:** Manual fix changelog for missing version ([`68a71ed`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/68a71ed76ae53d758f45aca70fa2a61bbbff5a9d))
### Refactor
* Changed dynamic imports to normal dependencies ([`5b0095f`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/5b0095f9121a92e1573415e08461561a8bd0e023))

## v0.1.1 (2023-04-11)
### Feature
* initial version of the bundler plugin. ([`adc7792`](https://github.com/educationwarehouse/edwh-bundler-plugin/commit/adc7792b8bbe2ee2e9326377f54f4010aa94d69c))
