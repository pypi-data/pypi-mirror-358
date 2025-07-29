# Changelog

## 0.1.0-alpha.7 (2025-06-27)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/stsak20/particle_sdk/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Features

* **client:** add support for aiohttp ([2804138](https://github.com/stsak20/particle_sdk/commit/280413870e3fe813c55b0bb9700b77c3f0d4d463))


### Bug Fixes

* **ci:** release-doctor — report correct token name ([0c8b088](https://github.com/stsak20/particle_sdk/commit/0c8b08881417982937eb33c95e24d1650b4c2793))
* **client:** correctly parse binary response | stream ([11381b6](https://github.com/stsak20/particle_sdk/commit/11381b697cfe449c61c5c703099d57d26e634e82))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([d703543](https://github.com/stsak20/particle_sdk/commit/d703543986be8a6af0bef7d4add846bfb8bd729d))


### Chores

* **ci:** enable for pull requests ([87c40e2](https://github.com/stsak20/particle_sdk/commit/87c40e2707cf8dba847aa9bfc4fc0607efc629b7))
* **internal:** update conftest.py ([f708725](https://github.com/stsak20/particle_sdk/commit/f70872507c81511eed13559071b8241eaa6c732c))
* **readme:** update badges ([8c8ef03](https://github.com/stsak20/particle_sdk/commit/8c8ef0352d34e525b2e486db06a773108541fece))
* **tests:** add tests for httpx client instantiation & proxies ([fda03e0](https://github.com/stsak20/particle_sdk/commit/fda03e03cf3da5a95b820e2debef15c46d54f6b7))
* **tests:** run tests in parallel ([7bd6913](https://github.com/stsak20/particle_sdk/commit/7bd6913aab3fa380aae3e6833a54aa2f894f998e))
* **tests:** skip some failing tests on the latest python versions ([10ed161](https://github.com/stsak20/particle_sdk/commit/10ed1616b10a87705c8e697d71c8fa420c60d8f1))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([68dda63](https://github.com/stsak20/particle_sdk/commit/68dda638d4332d39a415fc5fa4b179e4cd16e4f5))

## 0.1.0-alpha.6 (2025-06-03)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/stsak20/particle_sdk/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Features

* **client:** add follow_redirects request option ([2959ed7](https://github.com/stsak20/particle_sdk/commit/2959ed753e04f3c21bd26cb3f8d92df7b9b25f84))


### Chores

* **docs:** remove reference to rye shell ([db07575](https://github.com/stsak20/particle_sdk/commit/db07575cfd57c0522804191c2c253a9879632ac5))

## 0.1.0-alpha.5 (2025-05-28)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/stsak20/particle_sdk/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Bug Fixes

* **package:** support direct resource imports ([5c35097](https://github.com/stsak20/particle_sdk/commit/5c350978f6d534bf0626a63f051025ed8d541e11))


### Chores

* **ci:** fix installation instructions ([7c6bee2](https://github.com/stsak20/particle_sdk/commit/7c6bee271b9de85d17c3eda428c0eafc9627698d))
* **ci:** upload sdks to package manager ([6939bc9](https://github.com/stsak20/particle_sdk/commit/6939bc911944438bbf41d178baaf5de19d1043fa))
* **docs:** grammar improvements ([ddf1abb](https://github.com/stsak20/particle_sdk/commit/ddf1abb1f03e2e474cc5e1db23266a1e58cab4fc))
* **internal:** avoid errors for isinstance checks on proxies ([be10e09](https://github.com/stsak20/particle_sdk/commit/be10e0927489c463d5bde7bfd9579fb8ea01b7e1))
* **internal:** codegen related update ([31f73eb](https://github.com/stsak20/particle_sdk/commit/31f73eb5bfc3d7f6f894d36f7058b3e63c323d14))
* **internal:** codegen related update ([c6f708c](https://github.com/stsak20/particle_sdk/commit/c6f708cab21bed39b9818e04b62446ab648f3da2))
* **internal:** codegen related update ([003eafe](https://github.com/stsak20/particle_sdk/commit/003eafebfaa5aa2bf578a52da99d729ec214abe8))

## 0.1.0-alpha.4 (2025-05-07)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/stsak20/particle_sdk/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* **api:** added JWT Auth ([46277fd](https://github.com/stsak20/particle_sdk/commit/46277fdbe0795cf30f2e6d8d22657eee47d3d726))
* **api:** manual updates ([0260e4a](https://github.com/stsak20/particle_sdk/commit/0260e4a334b8f98a72ddb3e69d6f6d1fbf1433f9))


### Bug Fixes

* **api:** remove apikey auth ([826b00f](https://github.com/stsak20/particle_sdk/commit/826b00f652f08d8fea9f6806b88c948c1c517c5c))
* **api:** restructure deltas resource ([7c5a5e9](https://github.com/stsak20/particle_sdk/commit/7c5a5e94cc9849405d4fa2dc00166add2a924397))

## 0.1.0-alpha.3 (2025-04-29)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/stsak20/particle_sdk/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** manual updates ([12ca7bc](https://github.com/stsak20/particle_sdk/commit/12ca7bcc40e4094a74e42a777046a03c3a0151cb))
* **api:** manual updates ([f6c98a8](https://github.com/stsak20/particle_sdk/commit/f6c98a855fecd9a7c2b94b1365fd84ab0b74e7fd))


### Bug Fixes

* **api:** updated /deltas/R4/Patient/{particle_patient_id}/$everything endpoint ([b8a5ae0](https://github.com/stsak20/particle_sdk/commit/b8a5ae0c3a7b17c7db8271b933f9bd63602087f5))


### Chores

* **internal:** codegen related update ([bdac09d](https://github.com/stsak20/particle_sdk/commit/bdac09d39be80753a718b24d0b807d36535bc927))

## 0.1.0-alpha.2 (2025-04-29)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/stsak20/particle_sdk/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** update via SDK Studio ([7b353ba](https://github.com/stsak20/particle_sdk/commit/7b353bac4225b0f4d47944d4ff6326590279a5d7))
* **api:** update via SDK Studio ([c2ca43e](https://github.com/stsak20/particle_sdk/commit/c2ca43efe71ee9f4dc519fe9ddec0129750dca50))

## 0.1.0-alpha.1 (2025-04-29)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/stsak20/particle_sdk/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([a85deb8](https://github.com/stsak20/particle_sdk/commit/a85deb80b8228decc6cd158fe0cdc073443e764c))
* **api:** update via SDK Studio ([f6a4bb2](https://github.com/stsak20/particle_sdk/commit/f6a4bb2456ede53c03ef37f5b8b8c04686e1f104))
* **api:** update via SDK Studio ([4b00baa](https://github.com/stsak20/particle_sdk/commit/4b00baa0b49140759e6088fca4c92b2b134f9ba2))
* **api:** update via SDK Studio ([c9a74f7](https://github.com/stsak20/particle_sdk/commit/c9a74f7a0eb30a2e9b76ac18312b726076a5633f))


### Chores

* update SDK settings ([91a1e9f](https://github.com/stsak20/particle_sdk/commit/91a1e9f57ef4abe7cce157d659c5b72a964d985e))
* update SDK settings ([859638a](https://github.com/stsak20/particle_sdk/commit/859638a2ee27a8207d5b03620d6dcdd9d9f27b0f))
