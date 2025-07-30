# Changelog

## 0.9.0 (2025-06-28)

Full Changelog: [v0.8.2...v0.9.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.8.2...v0.9.0)

### Features

* **client:** add follow_redirects request option ([808cd98](https://github.com/masterpiecevr/mpx-sdk-python/commit/808cd9890eff9076dd0e11e0545f2a32facb0967))
* **client:** add support for aiohttp ([955c7ab](https://github.com/masterpiecevr/mpx-sdk-python/commit/955c7ab792ec3cce787a50331bab9d3a769455d4))


### Bug Fixes

* **ci:** release-doctor — report correct token name ([683e0f9](https://github.com/masterpiecevr/mpx-sdk-python/commit/683e0f917e16b74244c544e4d2d11b0881a02377))
* **client:** correctly parse binary response | stream ([1616be9](https://github.com/masterpiecevr/mpx-sdk-python/commit/1616be9f1ae15045926695f647b050eb4e030422))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([ab21b3f](https://github.com/masterpiecevr/mpx-sdk-python/commit/ab21b3fef8e1c76b1e479dd68ecc23678089761b))


### Chores

* **ci:** enable for pull requests ([872b2bf](https://github.com/masterpiecevr/mpx-sdk-python/commit/872b2bf009971a72cca0e6f627d53a67a90b3ff5))
* **ci:** fix installation instructions ([c211da7](https://github.com/masterpiecevr/mpx-sdk-python/commit/c211da7cae4ad494f05f549b67c52eb02cdcf7b3))
* **ci:** only run for pushes and fork pull requests ([ff2e9a1](https://github.com/masterpiecevr/mpx-sdk-python/commit/ff2e9a172567c63672cae445ce719415e2859779))
* **docs:** grammar improvements ([e27f379](https://github.com/masterpiecevr/mpx-sdk-python/commit/e27f3796ac47f7e1d18bf88a010a90cf47d1add1))
* **docs:** remove reference to rye shell ([cf7b399](https://github.com/masterpiecevr/mpx-sdk-python/commit/cf7b3996aafeb88a1a2044267ee68db61b085601))
* **docs:** remove unnecessary param examples ([09f8a3a](https://github.com/masterpiecevr/mpx-sdk-python/commit/09f8a3a2f33c03afe61e75b2dacb76e76c46e551))
* **internal:** update conftest.py ([3b6fd98](https://github.com/masterpiecevr/mpx-sdk-python/commit/3b6fd9871a9717aad59c0f605a4076610f3ea0ff))
* **readme:** update badges ([330e482](https://github.com/masterpiecevr/mpx-sdk-python/commit/330e48200d36103c9f4ab8ec6136ed59a2043aca))
* **tests:** add tests for httpx client instantiation & proxies ([a17a71d](https://github.com/masterpiecevr/mpx-sdk-python/commit/a17a71d999d2d7e67cdb956da180c8a791a4b394))
* **tests:** run tests in parallel ([de2fda6](https://github.com/masterpiecevr/mpx-sdk-python/commit/de2fda626a25e77c126682fc848508c03f404d1b))
* **tests:** skip some failing tests on the latest python versions ([3e4e7ff](https://github.com/masterpiecevr/mpx-sdk-python/commit/3e4e7ff1ed6a0e5c8d363b9214431863d85efadf))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([b0b8d58](https://github.com/masterpiecevr/mpx-sdk-python/commit/b0b8d58dd903033993cf89654008dfc1e932b019))

## 0.8.2 (2025-05-15)

Full Changelog: [v0.8.1...v0.8.2](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.8.1...v0.8.2)

### Bug Fixes

* **package:** support direct resource imports ([0e0ea0d](https://github.com/masterpiecevr/mpx-sdk-python/commit/0e0ea0d0da1b91626a5e876300659e4b4a128f79))
* **pydantic v1:** more robust ModelField.annotation check ([ee3f7e4](https://github.com/masterpiecevr/mpx-sdk-python/commit/ee3f7e453b3d118fc40a9c0cbc18205b2c710b3d))


### Chores

* broadly detect json family of content-type headers ([bcd6b58](https://github.com/masterpiecevr/mpx-sdk-python/commit/bcd6b58978bccd4df3c2460fcce2501460d0ecff))
* **ci:** add timeout thresholds for CI jobs ([af4d249](https://github.com/masterpiecevr/mpx-sdk-python/commit/af4d249d751851e617fe678a2d4cdc3f9a6de12b))
* **ci:** only use depot for staging repos ([fc19f7b](https://github.com/masterpiecevr/mpx-sdk-python/commit/fc19f7b71f41c13d93beecd8639277090159b161))
* **ci:** upload sdks to package manager ([6d5d431](https://github.com/masterpiecevr/mpx-sdk-python/commit/6d5d43169631c8cf64b87690cb75385c334afdda))
* **client:** minor internal fixes ([d47b5ac](https://github.com/masterpiecevr/mpx-sdk-python/commit/d47b5acdfbaa9351daa444fb30b60bc86dc82649))
* **internal:** avoid errors for isinstance checks on proxies ([03e9f30](https://github.com/masterpiecevr/mpx-sdk-python/commit/03e9f30eb6d45460d88dc705109dc83108546885))
* **internal:** base client updates ([b0538ea](https://github.com/masterpiecevr/mpx-sdk-python/commit/b0538eadab43a09db5b1f378d7ef24bed7167198))
* **internal:** bump pyright version ([3d1f1fb](https://github.com/masterpiecevr/mpx-sdk-python/commit/3d1f1fb534f6e23e26144561fb2f5afd0806ac72))
* **internal:** codegen related update ([669a3f0](https://github.com/masterpiecevr/mpx-sdk-python/commit/669a3f00fedcbd17aa9db439c682beb921f03206))
* **internal:** fix list file params ([19cfc49](https://github.com/masterpiecevr/mpx-sdk-python/commit/19cfc49fbc3f59b36c4c73894b3db980f68003d6))
* **internal:** import reformatting ([309ee52](https://github.com/masterpiecevr/mpx-sdk-python/commit/309ee52532ddd3478d7f25ecb796bc10f83278b5))
* **internal:** refactor retries to not use recursion ([3a5ffe8](https://github.com/masterpiecevr/mpx-sdk-python/commit/3a5ffe82a9ae9bc6100a54957d469b350e4aa0e6))
* **internal:** update models test ([bc4f6cc](https://github.com/masterpiecevr/mpx-sdk-python/commit/bc4f6cca65cc1b64415953dfd01d30a58854b052))
* **internal:** update pyright settings ([96142c8](https://github.com/masterpiecevr/mpx-sdk-python/commit/96142c804721dbb1c8191db4593928706c51f166))

## 0.8.1 (2025-04-12)

Full Changelog: [v0.8.0...v0.8.1](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.8.0...v0.8.1)

### Bug Fixes

* **perf:** optimize some hot paths ([52c5446](https://github.com/masterpiecevr/mpx-sdk-python/commit/52c5446fd803c8e6f4aea652d8dda59a2eb07fd1))
* **perf:** skip traversing types for NotGiven values ([05e5fa7](https://github.com/masterpiecevr/mpx-sdk-python/commit/05e5fa7aa25e92d4b9dc1bdde5da3604d3c0affa))


### Chores

* **internal:** expand CI branch coverage ([8357954](https://github.com/masterpiecevr/mpx-sdk-python/commit/83579549000a3992fb028e5110467f127a2c2878))
* **internal:** reduce CI branch coverage ([72a4c4c](https://github.com/masterpiecevr/mpx-sdk-python/commit/72a4c4c5c0059b1d315671e1e2b536fc2fe6815d))
* **internal:** remove trailing character ([#120](https://github.com/masterpiecevr/mpx-sdk-python/issues/120)) ([93390c0](https://github.com/masterpiecevr/mpx-sdk-python/commit/93390c05f0026faf4f2226eff5befe928cdf0c16))
* **internal:** slight transform perf improvement ([#122](https://github.com/masterpiecevr/mpx-sdk-python/issues/122)) ([8dfb373](https://github.com/masterpiecevr/mpx-sdk-python/commit/8dfb373343388790c316238e00c62284390b0cc7))

## 0.8.0 (2025-03-27)

Full Changelog: [v0.7.3...v0.8.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.7.3...v0.8.0)

### Features

* **api:** api update ([#118](https://github.com/masterpiecevr/mpx-sdk-python/issues/118)) ([0f04280](https://github.com/masterpiecevr/mpx-sdk-python/commit/0f0428068158540f848b43036734a54d4fdecfa5))


### Chores

* **internal:** avoid pytest-asyncio deprecation warning ([#74](https://github.com/masterpiecevr/mpx-sdk-python/issues/74)) ([c8d0075](https://github.com/masterpiecevr/mpx-sdk-python/commit/c8d00755e3eb031c965ee034be2dd68e37711d29))

## 0.7.3 (2025-03-27)

Full Changelog: [v0.7.2...v0.7.3](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.7.2...v0.7.3)

### Bug Fixes

* **ci:** remove publishing patch ([#113](https://github.com/masterpiecevr/mpx-sdk-python/issues/113)) ([4437672](https://github.com/masterpiecevr/mpx-sdk-python/commit/443767241776d7ca399d9ac615de1a0b59e49477))


### Chores

* fix typos ([#115](https://github.com/masterpiecevr/mpx-sdk-python/issues/115)) ([35d8469](https://github.com/masterpiecevr/mpx-sdk-python/commit/35d8469374ed702bcfbcf65c291565ca89f99844))

## 0.7.2 (2025-03-17)

Full Changelog: [v0.7.1...v0.7.2](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.7.1...v0.7.2)

### Bug Fixes

* **ci:** ensure pip is always available ([#110](https://github.com/masterpiecevr/mpx-sdk-python/issues/110)) ([0a7b30c](https://github.com/masterpiecevr/mpx-sdk-python/commit/0a7b30c6155570ab307fb498339303c9980d7546))

## 0.7.1 (2025-03-15)

Full Changelog: [v0.7.0...v0.7.1](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.7.0...v0.7.1)

### Bug Fixes

* **types:** handle more discriminated union shapes ([#108](https://github.com/masterpiecevr/mpx-sdk-python/issues/108)) ([42a562f](https://github.com/masterpiecevr/mpx-sdk-python/commit/42a562fc57196d58db25ebcf92572c91bcdb57b9))


### Chores

* **docs:** update client docstring ([#102](https://github.com/masterpiecevr/mpx-sdk-python/issues/102)) ([989a6f0](https://github.com/masterpiecevr/mpx-sdk-python/commit/989a6f09806a1759622ddd2647b69bb40f98602c))
* **internal:** bump rye to 0.44.0 ([#107](https://github.com/masterpiecevr/mpx-sdk-python/issues/107)) ([781077e](https://github.com/masterpiecevr/mpx-sdk-python/commit/781077e85b6184ee0038b9002156634cc4c448a6))
* **internal:** codegen related update ([#106](https://github.com/masterpiecevr/mpx-sdk-python/issues/106)) ([9bd9290](https://github.com/masterpiecevr/mpx-sdk-python/commit/9bd92902616a28eb48c26ac07e3c74579503d703))
* **internal:** fix devcontainers setup ([#98](https://github.com/masterpiecevr/mpx-sdk-python/issues/98)) ([3de63b2](https://github.com/masterpiecevr/mpx-sdk-python/commit/3de63b26ea37f9ae0a42c9f88d21c59c6a376daf))
* **internal:** properly set __pydantic_private__ ([#100](https://github.com/masterpiecevr/mpx-sdk-python/issues/100)) ([4675ec2](https://github.com/masterpiecevr/mpx-sdk-python/commit/4675ec20434787b7fce6734501d97da7d1a69020))
* **internal:** remove extra empty newlines ([#105](https://github.com/masterpiecevr/mpx-sdk-python/issues/105)) ([2f22013](https://github.com/masterpiecevr/mpx-sdk-python/commit/2f220131867a6ecc0dc23e59c07bc8905b3c540d))
* **internal:** remove unused http client options forwarding ([#103](https://github.com/masterpiecevr/mpx-sdk-python/issues/103)) ([dfe9b7c](https://github.com/masterpiecevr/mpx-sdk-python/commit/dfe9b7c9f5aeff2270938f213abadb30125a8662))


### Documentation

* update URLs from stainlessapi.com to stainless.com ([#101](https://github.com/masterpiecevr/mpx-sdk-python/issues/101)) ([9aa20b1](https://github.com/masterpiecevr/mpx-sdk-python/commit/9aa20b1e36794201f84a1d3d439a8fca22f5ec39))

## 0.7.0 (2025-02-21)

Full Changelog: [v0.6.0...v0.7.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.6.0...v0.7.0)

### Features

* **client:** allow passing `NotGiven` for body ([#95](https://github.com/masterpiecevr/mpx-sdk-python/issues/95)) ([123615a](https://github.com/masterpiecevr/mpx-sdk-python/commit/123615a5bcfd9f2c56ce4a840f3fdbda64a1ae6b))


### Bug Fixes

* **client:** mark some request bodies as optional ([123615a](https://github.com/masterpiecevr/mpx-sdk-python/commit/123615a5bcfd9f2c56ce4a840f3fdbda64a1ae6b))

## 0.6.0 (2025-02-14)

Full Changelog: [v0.5.0...v0.6.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.5.0...v0.6.0)

### Features

* **client:** send `X-Stainless-Read-Timeout` header ([#89](https://github.com/masterpiecevr/mpx-sdk-python/issues/89)) ([ad28d53](https://github.com/masterpiecevr/mpx-sdk-python/commit/ad28d539f04d72c51a49b61a2bf9156d5293cc85))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#93](https://github.com/masterpiecevr/mpx-sdk-python/issues/93)) ([c408045](https://github.com/masterpiecevr/mpx-sdk-python/commit/c408045610329f5cf16cd348532f953674131ad2))


### Chores

* **internal:** fix type traversing dictionary params ([#91](https://github.com/masterpiecevr/mpx-sdk-python/issues/91)) ([9d8d40a](https://github.com/masterpiecevr/mpx-sdk-python/commit/9d8d40aed74e3073ee3fcff944ac4773e91b3671))
* **internal:** minor type handling changes ([#92](https://github.com/masterpiecevr/mpx-sdk-python/issues/92)) ([7778b72](https://github.com/masterpiecevr/mpx-sdk-python/commit/7778b72cc55e8688de24e8ee40b82fe4af8d2814))

## 0.5.0 (2025-02-05)

Full Changelog: [v0.4.0...v0.5.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.4.0...v0.5.0)

### Features

* **api:** api update ([#87](https://github.com/masterpiecevr/mpx-sdk-python/issues/87)) ([10b521f](https://github.com/masterpiecevr/mpx-sdk-python/commit/10b521f85a4fb69b18054c09d1ba820359b611ca))


### Chores

* **internal:** bummp ruff dependency ([#86](https://github.com/masterpiecevr/mpx-sdk-python/issues/86)) ([32e29c1](https://github.com/masterpiecevr/mpx-sdk-python/commit/32e29c12c5db7c1fa9fe0f0bd301562b0b915b4e))
* **internal:** change default timeout to an int ([#85](https://github.com/masterpiecevr/mpx-sdk-python/issues/85)) ([4a7c6b2](https://github.com/masterpiecevr/mpx-sdk-python/commit/4a7c6b2eb9e1bedf0046fd5fb10d66263305132e))
* **internal:** minor formatting changes ([#84](https://github.com/masterpiecevr/mpx-sdk-python/issues/84)) ([97c82cb](https://github.com/masterpiecevr/mpx-sdk-python/commit/97c82cb701df709c210225fe4242a8a9deed0777))
* **internal:** minor style changes ([#82](https://github.com/masterpiecevr/mpx-sdk-python/issues/82)) ([0b87546](https://github.com/masterpiecevr/mpx-sdk-python/commit/0b87546e1d4903e2efcb8ef68bf2ef2c77824157))

## 0.4.0 (2025-01-22)

Full Changelog: [v0.3.0...v0.4.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.3.0...v0.4.0)

### Features

* **api:** api update ([#79](https://github.com/masterpiecevr/mpx-sdk-python/issues/79)) ([20099ab](https://github.com/masterpiecevr/mpx-sdk-python/commit/20099abd132260ba0e51bff637f917a159b54a94))

## 0.3.0 (2025-01-21)

Full Changelog: [v0.2.6...v0.3.0](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.2.6...v0.3.0)

### Features

* **api:** added text2image component ([#76](https://github.com/masterpiecevr/mpx-sdk-python/issues/76)) ([fa47371](https://github.com/masterpiecevr/mpx-sdk-python/commit/fa47371028623f1234e7fd84560960bcb27e4e95))

## 0.2.6 (2025-01-21)

Full Changelog: [v0.2.5...v0.2.6](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.2.5...v0.2.6)

### Bug Fixes

* **tests:** make test_get_platform less flaky ([#73](https://github.com/masterpiecevr/mpx-sdk-python/issues/73)) ([e334c61](https://github.com/masterpiecevr/mpx-sdk-python/commit/e334c61bc5fd09e32ab3e1e29ab3306502c8838a))


### Documentation

* **raw responses:** fix duplicate `the` ([#71](https://github.com/masterpiecevr/mpx-sdk-python/issues/71)) ([90753d8](https://github.com/masterpiecevr/mpx-sdk-python/commit/90753d88c1982631420ca818088593c5c1ee32e9))

## 0.2.5 (2025-01-17)

Full Changelog: [v0.2.4...v0.2.5](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.2.4...v0.2.5)

### Bug Fixes

* **client:** only call .close() when needed ([#66](https://github.com/masterpiecevr/mpx-sdk-python/issues/66)) ([ec4d9d6](https://github.com/masterpiecevr/mpx-sdk-python/commit/ec4d9d63b913a23e1b364d46048e4f768de9bc4d))


### Chores

* add missing isclass check ([#64](https://github.com/masterpiecevr/mpx-sdk-python/issues/64)) ([80d9491](https://github.com/masterpiecevr/mpx-sdk-python/commit/80d949160821c11139e6c170c2cc0e47e69505b9))
* added python examples ([04a55f8](https://github.com/masterpiecevr/mpx-sdk-python/commit/04a55f85230e11b13ecb2052ef9e9e48a7eab6c4))
* fixed lint issues with examples ([b74213f](https://github.com/masterpiecevr/mpx-sdk-python/commit/b74213f1c18e10ff8151ab556098506210ff2766))
* **internal:** bump httpx dependency ([#65](https://github.com/masterpiecevr/mpx-sdk-python/issues/65)) ([1c9485c](https://github.com/masterpiecevr/mpx-sdk-python/commit/1c9485cc6ccbfea7e4c0c589a75334475c288d76))
* **internal:** codegen related update ([#63](https://github.com/masterpiecevr/mpx-sdk-python/issues/63)) ([cf25d24](https://github.com/masterpiecevr/mpx-sdk-python/commit/cf25d2498663565ed03103f0ef20b5e6a4a996b6))
* **internal:** codegen related update ([#67](https://github.com/masterpiecevr/mpx-sdk-python/issues/67)) ([7f71528](https://github.com/masterpiecevr/mpx-sdk-python/commit/7f715283cdaf3827f547fcf71c641b6046e5d3dd))
* **internal:** codegen related update ([#68](https://github.com/masterpiecevr/mpx-sdk-python/issues/68)) ([223c661](https://github.com/masterpiecevr/mpx-sdk-python/commit/223c6610accef31b257ba8adc672116177a5cc87))
* **internal:** codegen related update ([#69](https://github.com/masterpiecevr/mpx-sdk-python/issues/69)) ([63d81b0](https://github.com/masterpiecevr/mpx-sdk-python/commit/63d81b0448d5baec6fa8aeade862e50b1ec13815))
* minor lint fixes ([d46c84c](https://github.com/masterpiecevr/mpx-sdk-python/commit/d46c84c65ecd90ce6982f32d8665b30d74940069))

## 0.2.4 (2024-12-20)

Full Changelog: [v0.2.0-beta.1...v0.2.4](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.2.0-beta.1...v0.2.4)

### Chores

* update SDK settings ([#59](https://github.com/masterpiecevr/mpx-sdk-python/issues/59)) ([9b07ec6](https://github.com/masterpiecevr/mpx-sdk-python/commit/9b07ec69d8ab20923b4ed238d51b7176c5acf2be))

## 0.2.0-beta.1 (2024-12-19)

Full Changelog: [v0.1.2-beta.6...v0.2.0-beta.1](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.2-beta.6...v0.2.0-beta.1)

### Features

* **api:** api update ([#57](https://github.com/masterpiecevr/mpx-sdk-python/issues/57)) ([7c02fb2](https://github.com/masterpiecevr/mpx-sdk-python/commit/7c02fb24ac2b95fd1ee00fddfd82156ce1343ace))


### Chores

* **internal:** fix some typos ([#55](https://github.com/masterpiecevr/mpx-sdk-python/issues/55)) ([725dc8f](https://github.com/masterpiecevr/mpx-sdk-python/commit/725dc8f21616c30aa2a706c3fe62cf2e1d91ff9a))

## 0.1.2-beta.6 (2024-12-17)

Full Changelog: [v0.1.2-beta.5...v0.1.2-beta.6](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.2-beta.5...v0.1.2-beta.6)

### Features

* **api:** api update ([#51](https://github.com/masterpiecevr/mpx-sdk-python/issues/51)) ([d660311](https://github.com/masterpiecevr/mpx-sdk-python/commit/d660311fa8ba76f1c88ed89eeb9ac2a3e5571630))


### Chores

* update SDK settings ([#53](https://github.com/masterpiecevr/mpx-sdk-python/issues/53)) ([76e2106](https://github.com/masterpiecevr/mpx-sdk-python/commit/76e210648fb32936aa4f7220c593647a14ef1b78))

## 0.1.2-beta.5 (2024-12-17)

Full Changelog: [v0.1.2-beta.4...v0.1.2-beta.5](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.2-beta.4...v0.1.2-beta.5)

### Features

* **api:** api update ([#45](https://github.com/masterpiecevr/mpx-sdk-python/issues/45)) ([035d151](https://github.com/masterpiecevr/mpx-sdk-python/commit/035d1512d39d9066fed954a995ec91860e24501f))
* **api:** api update ([#48](https://github.com/masterpiecevr/mpx-sdk-python/issues/48)) ([9dbe550](https://github.com/masterpiecevr/mpx-sdk-python/commit/9dbe550392e37f4bb2f7c9c1f4b526701cd812ef))


### Chores

* update SDK settings ([#43](https://github.com/masterpiecevr/mpx-sdk-python/issues/43)) ([a8a3e26](https://github.com/masterpiecevr/mpx-sdk-python/commit/a8a3e260ea46bd3d2c5bc75a25e220f1450cd589))
* update SDK settings ([#47](https://github.com/masterpiecevr/mpx-sdk-python/issues/47)) ([d919cc4](https://github.com/masterpiecevr/mpx-sdk-python/commit/d919cc4b28749f32423d4a6e659d7556bcb7aaf3))

## 0.1.2-beta.4 (2024-12-17)

Full Changelog: [v0.1.2-beta.3...v0.1.2-beta.4](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.2-beta.3...v0.1.2-beta.4)

### Features

* Update README.md ([35e9dec](https://github.com/masterpiecevr/mpx-sdk-python/commit/35e9decfe704c5f802ef6fe59a447e31f5d1b0a7))

## 0.1.2-beta.3 (2024-12-17)

Full Changelog: [v0.1.2-beta.1...v0.1.2-beta.3](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.2-beta.1...v0.1.2-beta.3)

### Features

* **api:** api update ([#28](https://github.com/masterpiecevr/mpx-sdk-python/issues/28)) ([a2ae388](https://github.com/masterpiecevr/mpx-sdk-python/commit/a2ae3880f54a6cf1cd7945dc661724f3b1c19781))
* **api:** api update ([#36](https://github.com/masterpiecevr/mpx-sdk-python/issues/36)) ([4959ee4](https://github.com/masterpiecevr/mpx-sdk-python/commit/4959ee49f2edce129f841c7b5e55838f4bf8cd66))
* **api:** api update ([#38](https://github.com/masterpiecevr/mpx-sdk-python/issues/38)) ([33346b7](https://github.com/masterpiecevr/mpx-sdk-python/commit/33346b79061c27fc5da3838ee5aad07cd09a3c38))


### Chores

* **internal:** codegen related update ([#30](https://github.com/masterpiecevr/mpx-sdk-python/issues/30)) ([5aa562e](https://github.com/masterpiecevr/mpx-sdk-python/commit/5aa562e5d921d04d7be9945b0d0def7789c4651d))
* **internal:** codegen related update ([#33](https://github.com/masterpiecevr/mpx-sdk-python/issues/33)) ([53a553f](https://github.com/masterpiecevr/mpx-sdk-python/commit/53a553ff88d73a34a559003b882b4acc27b08eb6))
* **internal:** codegen related update ([#34](https://github.com/masterpiecevr/mpx-sdk-python/issues/34)) ([1951923](https://github.com/masterpiecevr/mpx-sdk-python/commit/19519238d392eb31ebce597d23f702a7739f9197))
* **internal:** remove some duplicated imports ([#31](https://github.com/masterpiecevr/mpx-sdk-python/issues/31)) ([5361b97](https://github.com/masterpiecevr/mpx-sdk-python/commit/5361b97a6f310dcc51a1a37ae738ea326d0fc244))
* **internal:** updated imports ([#32](https://github.com/masterpiecevr/mpx-sdk-python/issues/32)) ([02ae04d](https://github.com/masterpiecevr/mpx-sdk-python/commit/02ae04deaaab004db6ea9463aceda592a7af9aff))
* update SDK settings ([#37](https://github.com/masterpiecevr/mpx-sdk-python/issues/37)) ([95c8273](https://github.com/masterpiecevr/mpx-sdk-python/commit/95c82734a00b6a496cb2f35ef2bdce3091e1b3bb))


### Documentation

* **readme:** example snippet for client context manager ([#35](https://github.com/masterpiecevr/mpx-sdk-python/issues/35)) ([cc66e22](https://github.com/masterpiecevr/mpx-sdk-python/commit/cc66e22a14705934b113d01e11da22cbb7ab0cdf))

## 0.1.2-beta.1 (2024-12-13)

Full Changelog: [v0.1.0-alpha.2...v0.1.2-beta.1](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.0-alpha.2...v0.1.2-beta.1)

### Features

* **api:** api update ([#24](https://github.com/masterpiecevr/mpx-sdk-python/issues/24)) ([d6205a3](https://github.com/masterpiecevr/mpx-sdk-python/commit/d6205a31cc2fca0c4d52d54dc17db1f73ceab798))
* **api:** api update ([#25](https://github.com/masterpiecevr/mpx-sdk-python/issues/25)) ([3bb6fa9](https://github.com/masterpiecevr/mpx-sdk-python/commit/3bb6fa98861d6febe27b76f4d68c00abc7b3d68e))


### Chores

* **internal:** codegen related update ([#22](https://github.com/masterpiecevr/mpx-sdk-python/issues/22)) ([e57801b](https://github.com/masterpiecevr/mpx-sdk-python/commit/e57801b9af8dc01816e0f158bccf6d018fa5bed9))
* update SDK settings ([#26](https://github.com/masterpiecevr/mpx-sdk-python/issues/26)) ([c32bf2f](https://github.com/masterpiecevr/mpx-sdk-python/commit/c32bf2f3c536829fe97aa8b1882289333a806e3d))

## 0.1.0-alpha.2 (2024-12-10)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** api update ([#20](https://github.com/masterpiecevr/mpx-sdk-python/issues/20)) ([1105030](https://github.com/masterpiecevr/mpx-sdk-python/commit/110503064a3b6cc4ed9f36901452168114de6a72))


### Chores

* **internal:** bump pydantic dependency ([#17](https://github.com/masterpiecevr/mpx-sdk-python/issues/17)) ([8f8436f](https://github.com/masterpiecevr/mpx-sdk-python/commit/8f8436fc220e7057250a969b5e8f44997cec9209))


### Documentation

* **readme:** fix http client proxies example ([#19](https://github.com/masterpiecevr/mpx-sdk-python/issues/19)) ([c9d15f8](https://github.com/masterpiecevr/mpx-sdk-python/commit/c9d15f85172c2d8ae692ab27fb7752b3c6b562a6))

## 0.1.0-alpha.1 (2024-12-05)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/masterpiecevr/mpx-sdk-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([3b6feec](https://github.com/masterpiecevr/mpx-sdk-python/commit/3b6feec7297318e819246db6bee7f95ccb84407c))
* **api:** update via SDK Studio ([a78d05c](https://github.com/masterpiecevr/mpx-sdk-python/commit/a78d05c46a0a4844d18ef51f19ee758fad90a649))
* **api:** update via SDK Studio ([230c272](https://github.com/masterpiecevr/mpx-sdk-python/commit/230c27212b67f3fb6b82e8ebd93f681b55672173))
* **api:** update via SDK Studio ([86bf274](https://github.com/masterpiecevr/mpx-sdk-python/commit/86bf2741d8ec7a17ea403c45873afb16d45c4e1a))
* **api:** update via SDK Studio ([7100a6a](https://github.com/masterpiecevr/mpx-sdk-python/commit/7100a6a7ab310bb6d283507bd436bc3750f4b69a))
* **api:** update via SDK Studio ([55a55ab](https://github.com/masterpiecevr/mpx-sdk-python/commit/55a55ab0c8d5d99233825f2a844d592536b37925))
* **api:** update via SDK Studio ([ffd0f4e](https://github.com/masterpiecevr/mpx-sdk-python/commit/ffd0f4e36f1932eefded16291f4e97b46164c4df))
* **api:** update via SDK Studio ([14d80f3](https://github.com/masterpiecevr/mpx-sdk-python/commit/14d80f3e90568f49b8d3cba52cc01194261d9615))
* **api:** update via SDK Studio ([0a83f26](https://github.com/masterpiecevr/mpx-sdk-python/commit/0a83f263940163b352ad9dbddcc0150d9082b403))
* **api:** update via SDK Studio ([5acc2e6](https://github.com/masterpiecevr/mpx-sdk-python/commit/5acc2e64a783dbc48fa31aef41c296d78e88b256))
* **api:** update via SDK Studio ([c020ecb](https://github.com/masterpiecevr/mpx-sdk-python/commit/c020ecb7e117637a10a9385894ba828ddf9c62db))
* **api:** update via SDK Studio ([f69e559](https://github.com/masterpiecevr/mpx-sdk-python/commit/f69e559cf8937bdbc9920b236ddad89fa110ad5b))
* **api:** update via SDK Studio ([4d1b4d5](https://github.com/masterpiecevr/mpx-sdk-python/commit/4d1b4d54f1c6923ac22bd508f9cd90adfda209a8))
* **api:** update via SDK Studio ([#14](https://github.com/masterpiecevr/mpx-sdk-python/issues/14)) ([bf73f9d](https://github.com/masterpiecevr/mpx-sdk-python/commit/bf73f9db3ff7c683d0e77271462074ddd510530a))
* **api:** update via SDK Studio ([#15](https://github.com/masterpiecevr/mpx-sdk-python/issues/15)) ([c24d40e](https://github.com/masterpiecevr/mpx-sdk-python/commit/c24d40e17704bb73c96e4f772d48fc4650979f4a))
* **api:** update via SDK Studio ([#3](https://github.com/masterpiecevr/mpx-sdk-python/issues/3)) ([3a89e78](https://github.com/masterpiecevr/mpx-sdk-python/commit/3a89e7809fc690eb2be4274995b4adcf0cdbd6d1))
* **api:** update via SDK Studio ([#4](https://github.com/masterpiecevr/mpx-sdk-python/issues/4)) ([aae6fd1](https://github.com/masterpiecevr/mpx-sdk-python/commit/aae6fd1f015d91392cf9cc956dc91d06d1b2a444))


### Bug Fixes

* **client:** compat with new httpx 0.28.0 release ([#11](https://github.com/masterpiecevr/mpx-sdk-python/issues/11)) ([b2da5bf](https://github.com/masterpiecevr/mpx-sdk-python/commit/b2da5bf6c8f6adc60906ae5b3e7db8bdb368d0c0))


### Chores

* go live ([#1](https://github.com/masterpiecevr/mpx-sdk-python/issues/1)) ([a99c91e](https://github.com/masterpiecevr/mpx-sdk-python/commit/a99c91eb215cc2f0157752f8b4bedf15fe807a73))
* go live ([#5](https://github.com/masterpiecevr/mpx-sdk-python/issues/5)) ([7b6c9ad](https://github.com/masterpiecevr/mpx-sdk-python/commit/7b6c9ad9fdc3f6983f6686ea7a63f82a659d58a6))
* **internal:** bump pyright ([#12](https://github.com/masterpiecevr/mpx-sdk-python/issues/12)) ([cd27786](https://github.com/masterpiecevr/mpx-sdk-python/commit/cd277866f8c9409f2f9dba954bd0d9bf0c410ac5))
* **internal:** exclude mypy from running on tests ([#10](https://github.com/masterpiecevr/mpx-sdk-python/issues/10)) ([7887c63](https://github.com/masterpiecevr/mpx-sdk-python/commit/7887c630fb3f30d6b980c742e0df2bed1b91ba49))
* **internal:** fix compat model_dump method when warnings are passed ([#7](https://github.com/masterpiecevr/mpx-sdk-python/issues/7)) ([87881fe](https://github.com/masterpiecevr/mpx-sdk-python/commit/87881feba0c66378408b084cfc9f2b72d7a7c05d))
* make the `Omit` type public ([#13](https://github.com/masterpiecevr/mpx-sdk-python/issues/13)) ([5cc34e4](https://github.com/masterpiecevr/mpx-sdk-python/commit/5cc34e49d959985bcc501d4837f96f0cc28b9995))
* rebuild project due to codegen change ([960aea0](https://github.com/masterpiecevr/mpx-sdk-python/commit/960aea0b4bc6aa1eaa9d49208ec1cb6f29f14246))
* rebuild project due to codegen change ([cdfd3df](https://github.com/masterpiecevr/mpx-sdk-python/commit/cdfd3df8203e5f800149c80d7f994eb87589e691))
* rebuild project due to codegen change ([faa065f](https://github.com/masterpiecevr/mpx-sdk-python/commit/faa065f6425af1a4b011fad66f8b6b50227c6cf2))
* rebuild project due to codegen change ([fc1e677](https://github.com/masterpiecevr/mpx-sdk-python/commit/fc1e677368020f8b4a3ca351c02114b9eaee2e64))
* remove now unused `cached-property` dep ([#9](https://github.com/masterpiecevr/mpx-sdk-python/issues/9)) ([a380e9b](https://github.com/masterpiecevr/mpx-sdk-python/commit/a380e9b52af186124b739b39d4c76212e644ea42))
* update SDK settings ([9c8b7ce](https://github.com/masterpiecevr/mpx-sdk-python/commit/9c8b7ce26345a29465804b2bf86eb8899d7c547a))


### Documentation

* add info log level to readme ([#8](https://github.com/masterpiecevr/mpx-sdk-python/issues/8)) ([229affb](https://github.com/masterpiecevr/mpx-sdk-python/commit/229affb60c23c31de8ecea13b8c6a362aa8a9029))
