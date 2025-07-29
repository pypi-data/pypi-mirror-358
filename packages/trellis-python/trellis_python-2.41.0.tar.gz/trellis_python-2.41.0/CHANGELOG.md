# Changelog

## 2.41.0 (2025-06-27)

Full Changelog: [v2.40.0...v2.41.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.40.0...v2.41.0)

### Features

* **client:** add follow_redirects request option ([910e61d](https://github.com/Trellis-insights/trellis-python-sdk/commit/910e61d6708f467b786088d5f8b765b1f6bec903))
* **client:** add support for aiohttp ([b9fa07b](https://github.com/Trellis-insights/trellis-python-sdk/commit/b9fa07b53cb9f841bff7132226e069111ec24417))


### Bug Fixes

* **ci:** release-doctor — report correct token name ([099dfeb](https://github.com/Trellis-insights/trellis-python-sdk/commit/099dfeb57471c6c291ef90bf980f2a95946502d5))
* **client:** correctly parse binary response | stream ([28dd1b0](https://github.com/Trellis-insights/trellis-python-sdk/commit/28dd1b06327051f9f779c7c15b95ba77e2e27991))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([0ac525e](https://github.com/Trellis-insights/trellis-python-sdk/commit/0ac525edfb40852d26c3604495a76062857995b3))


### Chores

* **ci:** enable for pull requests ([8fb3a29](https://github.com/Trellis-insights/trellis-python-sdk/commit/8fb3a29a0ca394ac837026d2dfe40282f393137b))
* **ci:** fix installation instructions ([34dd20b](https://github.com/Trellis-insights/trellis-python-sdk/commit/34dd20b322afc82a70d81c3352fdaccd4db58ad7))
* **ci:** upload sdks to package manager ([b8e6ac6](https://github.com/Trellis-insights/trellis-python-sdk/commit/b8e6ac608c2a045b17a4e07abd5901f7ed4eb4c0))
* **docs:** grammar improvements ([3da2e79](https://github.com/Trellis-insights/trellis-python-sdk/commit/3da2e7909c2a0950e7aab8063e057f2e11e7fa4b))
* **docs:** remove reference to rye shell ([1feea83](https://github.com/Trellis-insights/trellis-python-sdk/commit/1feea83c8ccbcb39446f2bb9561363f7d7f2ec2f))
* **docs:** remove unnecessary param examples ([ecc15f3](https://github.com/Trellis-insights/trellis-python-sdk/commit/ecc15f3de06436b382dfeb5bdfa00a4d2795b788))
* **internal:** update conftest.py ([ed03cb7](https://github.com/Trellis-insights/trellis-python-sdk/commit/ed03cb718d416223f236da97700a950126325d19))
* **readme:** update badges ([01678e5](https://github.com/Trellis-insights/trellis-python-sdk/commit/01678e582b98cf707a3f7d4b9235d55c7bb5319f))
* **tests:** add tests for httpx client instantiation & proxies ([b8d60c8](https://github.com/Trellis-insights/trellis-python-sdk/commit/b8d60c86d34fce43d8dd80c1bc54f319f9337de5))
* **tests:** run tests in parallel ([c1e9e09](https://github.com/Trellis-insights/trellis-python-sdk/commit/c1e9e09f20b6445f6f18e79d5916b622b1df0a36))
* **tests:** skip some failing tests on the latest python versions ([5609282](https://github.com/Trellis-insights/trellis-python-sdk/commit/56092824c7fc618759986b0dd90db79da0ea65e4))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([462f50f](https://github.com/Trellis-insights/trellis-python-sdk/commit/462f50fcca1dbadd13700b3195d8fc76a2338dc6))

## 2.40.0 (2025-05-14)

Full Changelog: [v2.39.0...v2.40.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.39.0...v2.40.0)

### Features

* **api:** api update ([8b4af2a](https://github.com/Trellis-insights/trellis-python-sdk/commit/8b4af2a1f0dd0de4e5f47623689154b65097138a))
* **api:** api update ([a75e9f4](https://github.com/Trellis-insights/trellis-python-sdk/commit/a75e9f4404e5114ef0941555f067ced468fa5fb8))


### Bug Fixes

* **package:** support direct resource imports ([b190356](https://github.com/Trellis-insights/trellis-python-sdk/commit/b190356b1fa9a0ac8bbf3d6add83d574921206a1))
* **pydantic v1:** more robust ModelField.annotation check ([f71c48c](https://github.com/Trellis-insights/trellis-python-sdk/commit/f71c48c28ffab45d6dc6e0da400f475d7c8240de))


### Chores

* broadly detect json family of content-type headers ([c371395](https://github.com/Trellis-insights/trellis-python-sdk/commit/c3713950a42da45160d49d5430607cec1166cdf8))
* **ci:** add timeout thresholds for CI jobs ([408a8de](https://github.com/Trellis-insights/trellis-python-sdk/commit/408a8de4323da4d8f9a7b6e564f656af9ffde387))
* **ci:** only use depot for staging repos ([3bb6cb8](https://github.com/Trellis-insights/trellis-python-sdk/commit/3bb6cb82916d56f737e74db06d7efa559e214a80))
* **internal:** avoid errors for isinstance checks on proxies ([1d0e3e0](https://github.com/Trellis-insights/trellis-python-sdk/commit/1d0e3e0c55b4d49899c2c0edc421712346ba2f41))
* **internal:** codegen related update ([708fdec](https://github.com/Trellis-insights/trellis-python-sdk/commit/708fdec68a84ed76fb39df7e2d4e74eed9130614))
* **internal:** fix list file params ([4167678](https://github.com/Trellis-insights/trellis-python-sdk/commit/4167678adf509654179a7f7dabdb4c498ebd9fae))
* **internal:** import reformatting ([077344a](https://github.com/Trellis-insights/trellis-python-sdk/commit/077344acbedab9251b77e1fb75e4261397ecbfa9))
* **internal:** minor formatting changes ([bbfc41e](https://github.com/Trellis-insights/trellis-python-sdk/commit/bbfc41edf505134e53dcc38ffacc9455ca962de4))
* **internal:** refactor retries to not use recursion ([d6effd6](https://github.com/Trellis-insights/trellis-python-sdk/commit/d6effd68cb341d9caf272155af819fac6870d258))
* **internal:** update models test ([17bdb44](https://github.com/Trellis-insights/trellis-python-sdk/commit/17bdb447a15ab1e17731c4f521603180a30dddb9))

## 2.39.0 (2025-04-17)

Full Changelog: [v2.38.0...v2.39.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.38.0...v2.39.0)

### Features

* **api:** api update ([b603fc7](https://github.com/Trellis-insights/trellis-python-sdk/commit/b603fc741d51505dea7a0db8ac919682567fa78e))


### Bug Fixes

* **perf:** optimize some hot paths ([7cc1e85](https://github.com/Trellis-insights/trellis-python-sdk/commit/7cc1e8541e775a3251cf49b6b77e81f71cbeb2ea))
* **perf:** skip traversing types for NotGiven values ([10ac1b6](https://github.com/Trellis-insights/trellis-python-sdk/commit/10ac1b6c4b0d440cb24086b4d366c21f60b84e2c))


### Chores

* **client:** minor internal fixes ([4b46082](https://github.com/Trellis-insights/trellis-python-sdk/commit/4b46082b518ac8dcbc3d88212bd04d2e3ba296b5))
* **internal:** base client updates ([f2e22ea](https://github.com/Trellis-insights/trellis-python-sdk/commit/f2e22eabff8922de10da3003bcd219edd79b2047))
* **internal:** bump pyright version ([77ee35d](https://github.com/Trellis-insights/trellis-python-sdk/commit/77ee35d4566bbad223a5c43bd4df0f4216ac883a))
* **internal:** expand CI branch coverage ([353dd40](https://github.com/Trellis-insights/trellis-python-sdk/commit/353dd40f112c9429fb68b7faf3f3c114b60db137))
* **internal:** reduce CI branch coverage ([5bee921](https://github.com/Trellis-insights/trellis-python-sdk/commit/5bee921719b88bae4902247dcffeb92c1975ba12))
* **internal:** slight transform perf improvement ([#201](https://github.com/Trellis-insights/trellis-python-sdk/issues/201)) ([4f73d89](https://github.com/Trellis-insights/trellis-python-sdk/commit/4f73d89b222affa1de2e01c65d062386d129a5c3))
* **internal:** update pyright settings ([c17a748](https://github.com/Trellis-insights/trellis-python-sdk/commit/c17a748035f551663b538472ffc611dba7b467f2))

## 2.38.0 (2025-04-04)

Full Changelog: [v2.37.0...v2.38.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.37.0...v2.38.0)

### Features

* **api:** api update ([#199](https://github.com/Trellis-insights/trellis-python-sdk/issues/199)) ([a169e79](https://github.com/Trellis-insights/trellis-python-sdk/commit/a169e79a01a29aa1d05b2b3b0b010543c1859d56))


### Chores

* **internal:** remove trailing character ([#197](https://github.com/Trellis-insights/trellis-python-sdk/issues/197)) ([1ee04ca](https://github.com/Trellis-insights/trellis-python-sdk/commit/1ee04caeeb0d477a2fb0ff89d83bb3c3d0d02d7d))

## 2.37.0 (2025-04-02)

Full Changelog: [v2.36.0...v2.37.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.36.0...v2.37.0)

### Features

* **api:** api update ([#194](https://github.com/Trellis-insights/trellis-python-sdk/issues/194)) ([aa390c4](https://github.com/Trellis-insights/trellis-python-sdk/commit/aa390c4e248fb056ebe34e97bb5137891c627257))

## 2.36.0 (2025-03-27)

Full Changelog: [v2.35.0...v2.36.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.35.0...v2.36.0)

### Features

* **api:** api update ([#192](https://github.com/Trellis-insights/trellis-python-sdk/issues/192)) ([820b861](https://github.com/Trellis-insights/trellis-python-sdk/commit/820b86119211776715ace58a5ad5bfb3fe3d2661))


### Chores

* fix typos ([#190](https://github.com/Trellis-insights/trellis-python-sdk/issues/190)) ([8605f71](https://github.com/Trellis-insights/trellis-python-sdk/commit/8605f7192eccd0f156496d92f69b6e4b7f26343d))

## 2.35.0 (2025-03-26)

Full Changelog: [v2.34.0...v2.35.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.34.0...v2.35.0)

### Features

* **api:** api update ([#187](https://github.com/Trellis-insights/trellis-python-sdk/issues/187)) ([e5ad204](https://github.com/Trellis-insights/trellis-python-sdk/commit/e5ad2047e21a2f0e333ca7d128acd8d4aff03189))

## 2.34.0 (2025-03-21)

Full Changelog: [v2.33.0...v2.34.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.33.0...v2.34.0)

### Features

* **api:** api update ([#184](https://github.com/Trellis-insights/trellis-python-sdk/issues/184)) ([a133fab](https://github.com/Trellis-insights/trellis-python-sdk/commit/a133fab489fd3b6243c4883b56f1d1259a2d3a71))

## 2.33.0 (2025-03-19)

Full Changelog: [v2.32.1...v2.33.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.32.1...v2.33.0)

### Features

* **api:** api update ([#182](https://github.com/Trellis-insights/trellis-python-sdk/issues/182)) ([4f2afaf](https://github.com/Trellis-insights/trellis-python-sdk/commit/4f2afafb99207592b74c4399f2b3fb8badb1d8e1))


### Bug Fixes

* **ci:** ensure pip is always available ([#179](https://github.com/Trellis-insights/trellis-python-sdk/issues/179)) ([9ff193b](https://github.com/Trellis-insights/trellis-python-sdk/commit/9ff193b088ea62539833aa2dc0a02cb29c0950ab))
* **ci:** remove publishing patch ([#181](https://github.com/Trellis-insights/trellis-python-sdk/issues/181)) ([a4f9a19](https://github.com/Trellis-insights/trellis-python-sdk/commit/a4f9a19e9e1903814f8237b4ceaeb051169e2691))

## 2.32.1 (2025-03-15)

Full Changelog: [v2.32.0...v2.32.1](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.32.0...v2.32.1)

### Bug Fixes

* **types:** handle more discriminated union shapes ([#177](https://github.com/Trellis-insights/trellis-python-sdk/issues/177)) ([646929b](https://github.com/Trellis-insights/trellis-python-sdk/commit/646929bf3773369ae2a25962701e47cecd58ebff))


### Chores

* **internal:** bump rye to 0.44.0 ([#176](https://github.com/Trellis-insights/trellis-python-sdk/issues/176)) ([11e4db1](https://github.com/Trellis-insights/trellis-python-sdk/commit/11e4db15f7ee9f431a2d4931a496fc2ec5d2db73))
* **internal:** codegen related update ([#175](https://github.com/Trellis-insights/trellis-python-sdk/issues/175)) ([57dcab6](https://github.com/Trellis-insights/trellis-python-sdk/commit/57dcab6995b339c0831c5d7c681ffd8b4b9f0d03))
* **internal:** remove extra empty newlines ([#173](https://github.com/Trellis-insights/trellis-python-sdk/issues/173)) ([b006d0e](https://github.com/Trellis-insights/trellis-python-sdk/commit/b006d0e11c791a9eec1db70190e0447e8f2e7fce))

## 2.32.0 (2025-03-13)

Full Changelog: [v2.31.0...v2.32.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.31.0...v2.32.0)

### Features

* **api:** api update ([#171](https://github.com/Trellis-insights/trellis-python-sdk/issues/171)) ([e787a1b](https://github.com/Trellis-insights/trellis-python-sdk/commit/e787a1b123d38fde4317545da8a67a2141071744))


### Documentation

* revise readme docs about nested params ([#168](https://github.com/Trellis-insights/trellis-python-sdk/issues/168)) ([1b83500](https://github.com/Trellis-insights/trellis-python-sdk/commit/1b83500f295106f5ae6372bef8e16a1430e9391d))

## 2.31.0 (2025-03-11)

Full Changelog: [v2.30.0...v2.31.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.30.0...v2.31.0)

### Features

* **api:** api update ([#165](https://github.com/Trellis-insights/trellis-python-sdk/issues/165)) ([00a2fa1](https://github.com/Trellis-insights/trellis-python-sdk/commit/00a2fa169fac64cd14f0b74f85a1675fa9ae1406))

## 2.30.0 (2025-03-07)

Full Changelog: [v2.29.0...v2.30.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.29.0...v2.30.0)

### Features

* **api:** api update ([#162](https://github.com/Trellis-insights/trellis-python-sdk/issues/162)) ([c4fe32d](https://github.com/Trellis-insights/trellis-python-sdk/commit/c4fe32d3a499a05f38bcf8fac94efe0d966352a3))

## 2.29.0 (2025-03-05)

Full Changelog: [v2.28.0...v2.29.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.28.0...v2.29.0)

### Features

* **api:** api update ([#160](https://github.com/Trellis-insights/trellis-python-sdk/issues/160)) ([8f607d3](https://github.com/Trellis-insights/trellis-python-sdk/commit/8f607d3cd564776ffca53044b9ebaae51d589f9b))


### Chores

* **internal:** remove unused http client options forwarding ([#158](https://github.com/Trellis-insights/trellis-python-sdk/issues/158)) ([d057d14](https://github.com/Trellis-insights/trellis-python-sdk/commit/d057d14297d949b20d1490267a61096518a526d5))

## 2.28.0 (2025-03-01)

Full Changelog: [v2.27.0...v2.28.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.27.0...v2.28.0)

### Features

* **api:** api update ([#156](https://github.com/Trellis-insights/trellis-python-sdk/issues/156)) ([c85ff9d](https://github.com/Trellis-insights/trellis-python-sdk/commit/c85ff9da3ee928a60b3a5410265a227e2b3a43fe))


### Chores

* **docs:** update client docstring ([#155](https://github.com/Trellis-insights/trellis-python-sdk/issues/155)) ([3f49987](https://github.com/Trellis-insights/trellis-python-sdk/commit/3f499874ef2022eee90601fa28db6a40ea37cc87))
* **internal:** fix devcontainers setup ([#151](https://github.com/Trellis-insights/trellis-python-sdk/issues/151)) ([4340fc7](https://github.com/Trellis-insights/trellis-python-sdk/commit/4340fc74ec6d51b502a62eff2a676946d17cdc7a))
* **internal:** properly set __pydantic_private__ ([#153](https://github.com/Trellis-insights/trellis-python-sdk/issues/153)) ([3ad7274](https://github.com/Trellis-insights/trellis-python-sdk/commit/3ad7274c348f37dc8f930168706ebba5c76e9477))


### Documentation

* update URLs from stainlessapi.com to stainless.com ([#154](https://github.com/Trellis-insights/trellis-python-sdk/issues/154)) ([a565767](https://github.com/Trellis-insights/trellis-python-sdk/commit/a5657670d04eaf6eca50d7c8765fd347a2e92c99))

## 2.27.0 (2025-02-21)

Full Changelog: [v2.26.0...v2.27.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.26.0...v2.27.0)

### Features

* **client:** allow passing `NotGiven` for body ([#149](https://github.com/Trellis-insights/trellis-python-sdk/issues/149)) ([28e797e](https://github.com/Trellis-insights/trellis-python-sdk/commit/28e797e04eccb6c5286ff6acaa51fd5a7e98e815))


### Bug Fixes

* **client:** mark some request bodies as optional ([28e797e](https://github.com/Trellis-insights/trellis-python-sdk/commit/28e797e04eccb6c5286ff6acaa51fd5a7e98e815))


### Chores

* **internal:** codegen related update ([#147](https://github.com/Trellis-insights/trellis-python-sdk/issues/147)) ([de4bfc3](https://github.com/Trellis-insights/trellis-python-sdk/commit/de4bfc3a4debffbe682c27c9d6b4466cc9c8e94a))

## 2.26.0 (2025-02-14)

Full Changelog: [v2.25.0...v2.26.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.25.0...v2.26.0)

### Features

* **client:** send `X-Stainless-Read-Timeout` header ([#140](https://github.com/Trellis-insights/trellis-python-sdk/issues/140)) ([1361222](https://github.com/Trellis-insights/trellis-python-sdk/commit/136122249bf0fcee69abfbee45f99cbcf1747c39))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#145](https://github.com/Trellis-insights/trellis-python-sdk/issues/145)) ([05fcf8f](https://github.com/Trellis-insights/trellis-python-sdk/commit/05fcf8f700b4fef199a041e0ddcc08a2928e0a23))


### Chores

* **internal:** fix type traversing dictionary params ([#142](https://github.com/Trellis-insights/trellis-python-sdk/issues/142)) ([f336af1](https://github.com/Trellis-insights/trellis-python-sdk/commit/f336af1ec14773e7f271d2153252894a992b83cc))
* **internal:** minor type handling changes ([#143](https://github.com/Trellis-insights/trellis-python-sdk/issues/143)) ([b248179](https://github.com/Trellis-insights/trellis-python-sdk/commit/b2481799ee56d3f22be77a666a451b2e5994d79c))
* **internal:** update client tests ([#144](https://github.com/Trellis-insights/trellis-python-sdk/issues/144)) ([3632be1](https://github.com/Trellis-insights/trellis-python-sdk/commit/3632be1e7d3635b672ea3f73cb6fae85ab335955))

## 2.25.0 (2025-02-05)

Full Changelog: [v2.24.0...v2.25.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.24.0...v2.25.0)

### Features

* **api:** api update ([#138](https://github.com/Trellis-insights/trellis-python-sdk/issues/138)) ([b4311a8](https://github.com/Trellis-insights/trellis-python-sdk/commit/b4311a8ad74ef16686374cd18133f012049742d7))


### Chores

* **internal:** bummp ruff dependency ([#137](https://github.com/Trellis-insights/trellis-python-sdk/issues/137)) ([01039a7](https://github.com/Trellis-insights/trellis-python-sdk/commit/01039a7e9b60eff2126865013d144f58c3287f43))
* **internal:** change default timeout to an int ([#135](https://github.com/Trellis-insights/trellis-python-sdk/issues/135)) ([e230bfc](https://github.com/Trellis-insights/trellis-python-sdk/commit/e230bfc3af422e69aa7b5e5e2cc00fcc53c1986d))

## 2.24.0 (2025-01-29)

Full Changelog: [v2.23.0...v2.24.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.23.0...v2.24.0)

### Features

* **api:** api update ([#133](https://github.com/Trellis-insights/trellis-python-sdk/issues/133)) ([472d680](https://github.com/Trellis-insights/trellis-python-sdk/commit/472d680d9b40004abd2b81f9d2e5cf3096591ddc))


### Chores

* **internal:** codegen related update ([#129](https://github.com/Trellis-insights/trellis-python-sdk/issues/129)) ([e3a810a](https://github.com/Trellis-insights/trellis-python-sdk/commit/e3a810a2516553e34f4ea14c4870cc032145c889))
* **internal:** codegen related update ([#132](https://github.com/Trellis-insights/trellis-python-sdk/issues/132)) ([0e990f1](https://github.com/Trellis-insights/trellis-python-sdk/commit/0e990f119f23c2fa238668dfe47abf015586c682))
* **internal:** minor formatting changes ([#131](https://github.com/Trellis-insights/trellis-python-sdk/issues/131)) ([3197be7](https://github.com/Trellis-insights/trellis-python-sdk/commit/3197be745157b046c8d92b91cca2cc6b69a93b43))

## 2.23.0 (2025-01-22)

Full Changelog: [v2.22.1...v2.23.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.22.1...v2.23.0)

### Features

* **api:** api update ([#126](https://github.com/Trellis-insights/trellis-python-sdk/issues/126)) ([395c2c7](https://github.com/Trellis-insights/trellis-python-sdk/commit/395c2c739b89b435a0af4b5e794ebc1edba92b3f))

## 2.22.1 (2025-01-21)

Full Changelog: [v2.22.0...v2.22.1](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.22.0...v2.22.1)

### Bug Fixes

* **tests:** make test_get_platform less flaky ([#123](https://github.com/Trellis-insights/trellis-python-sdk/issues/123)) ([2d4a5bf](https://github.com/Trellis-insights/trellis-python-sdk/commit/2d4a5bf3c19d76f7acf3c62c7730ae3a18ddbb57))


### Documentation

* **raw responses:** fix duplicate `the` ([#121](https://github.com/Trellis-insights/trellis-python-sdk/issues/121)) ([80e1c8a](https://github.com/Trellis-insights/trellis-python-sdk/commit/80e1c8aa9c3fcf324939b3ad193f6054b058c881))

## 2.22.0 (2025-01-17)

Full Changelog: [v2.21.0...v2.22.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.21.0...v2.22.0)

### Features

* **api:** api update ([#119](https://github.com/Trellis-insights/trellis-python-sdk/issues/119)) ([45b9c20](https://github.com/Trellis-insights/trellis-python-sdk/commit/45b9c209368a0095ee105f42e7381693f484bac2))


### Chores

* **internal:** codegen related update ([#117](https://github.com/Trellis-insights/trellis-python-sdk/issues/117)) ([d5fc641](https://github.com/Trellis-insights/trellis-python-sdk/commit/d5fc641837dc7f8b02751061c018044a22fab2a7))

## 2.21.0 (2025-01-17)

Full Changelog: [v2.20.0...v2.21.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.20.0...v2.21.0)

### Features

* **api:** api update ([#114](https://github.com/Trellis-insights/trellis-python-sdk/issues/114)) ([d42f7fa](https://github.com/Trellis-insights/trellis-python-sdk/commit/d42f7fac74bee65814de2a651d8c30430c230493))

## 2.20.0 (2025-01-16)

Full Changelog: [v2.19.2...v2.20.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.19.2...v2.20.0)

### Features

* **api:** api update ([#111](https://github.com/Trellis-insights/trellis-python-sdk/issues/111)) ([cbf544e](https://github.com/Trellis-insights/trellis-python-sdk/commit/cbf544e87446c436d339456ff96a4cb52a43cfef))

## 2.19.2 (2025-01-10)

Full Changelog: [v2.19.1...v2.19.2](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.19.1...v2.19.2)

### Bug Fixes

* correctly handle deserialising `cls` fields ([#109](https://github.com/Trellis-insights/trellis-python-sdk/issues/109)) ([abc795c](https://github.com/Trellis-insights/trellis-python-sdk/commit/abc795c6afc84ad2323e00ad1cc1f29a3f9ee16f))


### Chores

* **internal:** codegen related update ([#108](https://github.com/Trellis-insights/trellis-python-sdk/issues/108)) ([1b9f3e8](https://github.com/Trellis-insights/trellis-python-sdk/commit/1b9f3e8129eee40ffb7ed9d1c3d0c0fd19f1ff27))


### Documentation

* fix typos ([#106](https://github.com/Trellis-insights/trellis-python-sdk/issues/106)) ([a5f2a47](https://github.com/Trellis-insights/trellis-python-sdk/commit/a5f2a47708058c90825ecd3f3100cd548661ee51))

## 2.19.1 (2025-01-09)

Full Changelog: [v2.19.0...v2.19.1](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.19.0...v2.19.1)

### Bug Fixes

* **client:** only call .close() when needed ([#103](https://github.com/Trellis-insights/trellis-python-sdk/issues/103)) ([e01e840](https://github.com/Trellis-insights/trellis-python-sdk/commit/e01e84073a7f6ae8857213f1bf8c9d2e5bbee714))

## 2.19.0 (2025-01-09)

Full Changelog: [v2.18.0...v2.19.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.18.0...v2.19.0)

### Features

* **api:** api update ([#101](https://github.com/Trellis-insights/trellis-python-sdk/issues/101)) ([037b59b](https://github.com/Trellis-insights/trellis-python-sdk/commit/037b59b9e8cfce5be42ed2016f003ed8630f61ff))


### Chores

* add missing isclass check ([#99](https://github.com/Trellis-insights/trellis-python-sdk/issues/99)) ([097a301](https://github.com/Trellis-insights/trellis-python-sdk/commit/097a301877cac6e3425b1de8a2f08491619bda94))
* **internal:** bump httpx dependency ([#100](https://github.com/Trellis-insights/trellis-python-sdk/issues/100)) ([ae53692](https://github.com/Trellis-insights/trellis-python-sdk/commit/ae536924ce1103d43611275f00f6eec7d101aa01))
* **internal:** codegen related update ([#89](https://github.com/Trellis-insights/trellis-python-sdk/issues/89)) ([5e088aa](https://github.com/Trellis-insights/trellis-python-sdk/commit/5e088aa56b381d06e8d850754d9168faba1fd352))
* **internal:** codegen related update ([#91](https://github.com/Trellis-insights/trellis-python-sdk/issues/91)) ([baf04fb](https://github.com/Trellis-insights/trellis-python-sdk/commit/baf04fbc4e152d8e2c4e02b753ac03af2457cc73))
* **internal:** codegen related update ([#92](https://github.com/Trellis-insights/trellis-python-sdk/issues/92)) ([193bbe7](https://github.com/Trellis-insights/trellis-python-sdk/commit/193bbe7ed842185e52830ecd59a89d40121ea0c1))
* **internal:** codegen related update ([#93](https://github.com/Trellis-insights/trellis-python-sdk/issues/93)) ([c69735b](https://github.com/Trellis-insights/trellis-python-sdk/commit/c69735be76fcfbff5cf86f22d1add40a8be930fe))
* **internal:** codegen related update ([#94](https://github.com/Trellis-insights/trellis-python-sdk/issues/94)) ([1dcfad5](https://github.com/Trellis-insights/trellis-python-sdk/commit/1dcfad5af12a89be1b50f5e566bc9a69fb090a64))
* **internal:** codegen related update ([#95](https://github.com/Trellis-insights/trellis-python-sdk/issues/95)) ([eb917d9](https://github.com/Trellis-insights/trellis-python-sdk/commit/eb917d9de234aa5e6c6aaf0cad57bd3b43d8fdaa))
* **internal:** codegen related update ([#96](https://github.com/Trellis-insights/trellis-python-sdk/issues/96)) ([1211273](https://github.com/Trellis-insights/trellis-python-sdk/commit/1211273c260250ded0f5c770a650fd47b06e1ac8))
* **internal:** codegen related update ([#98](https://github.com/Trellis-insights/trellis-python-sdk/issues/98)) ([7d5ce96](https://github.com/Trellis-insights/trellis-python-sdk/commit/7d5ce963c9a7cc38e9c7c376cdf05c4e9535d99a))
* **internal:** fix some typos ([#97](https://github.com/Trellis-insights/trellis-python-sdk/issues/97)) ([e1329ef](https://github.com/Trellis-insights/trellis-python-sdk/commit/e1329ef6079661a663ab9d7f56f758a0602eab02))

## 2.18.0 (2024-12-18)

Full Changelog: [v2.17.0...v2.18.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.17.0...v2.18.0)

### Features

* **api:** api update ([#87](https://github.com/Trellis-insights/trellis-python-sdk/issues/87)) ([4636e88](https://github.com/Trellis-insights/trellis-python-sdk/commit/4636e88fcdf297d158660f41ad417205f1e49cf6))


### Chores

* **internal:** add support for TypeAliasType ([#76](https://github.com/Trellis-insights/trellis-python-sdk/issues/76)) ([e225b9a](https://github.com/Trellis-insights/trellis-python-sdk/commit/e225b9afcdf20fc795444b7af864468dfcf0a913))
* **internal:** bump pyright ([#74](https://github.com/Trellis-insights/trellis-python-sdk/issues/74)) ([5eee456](https://github.com/Trellis-insights/trellis-python-sdk/commit/5eee456fcbc96ec0cb61ea8331c0c2841a72e9b7))
* **internal:** codegen related update ([#77](https://github.com/Trellis-insights/trellis-python-sdk/issues/77)) ([7b28a89](https://github.com/Trellis-insights/trellis-python-sdk/commit/7b28a8934b49c4c100d8e52b14eb1a7987952c3a))
* **internal:** codegen related update ([#78](https://github.com/Trellis-insights/trellis-python-sdk/issues/78)) ([e293027](https://github.com/Trellis-insights/trellis-python-sdk/commit/e2930277e86639ae1f6172a1d28605e65e624e57))
* **internal:** codegen related update ([#79](https://github.com/Trellis-insights/trellis-python-sdk/issues/79)) ([5b28aff](https://github.com/Trellis-insights/trellis-python-sdk/commit/5b28affd6a5e9788d2cf11450d7427ba18293b10))
* **internal:** codegen related update ([#80](https://github.com/Trellis-insights/trellis-python-sdk/issues/80)) ([750e540](https://github.com/Trellis-insights/trellis-python-sdk/commit/750e540e770c032ed57ba59f1e6547f6b8321de1))
* **internal:** codegen related update ([#81](https://github.com/Trellis-insights/trellis-python-sdk/issues/81)) ([bbb228e](https://github.com/Trellis-insights/trellis-python-sdk/commit/bbb228e2009fb25911c7bc006b50d6756b2b9515))
* **internal:** codegen related update ([#82](https://github.com/Trellis-insights/trellis-python-sdk/issues/82)) ([731f370](https://github.com/Trellis-insights/trellis-python-sdk/commit/731f370df67ff57b1620f24f0af6041130cded91))
* **internal:** codegen related update ([#85](https://github.com/Trellis-insights/trellis-python-sdk/issues/85)) ([df550ea](https://github.com/Trellis-insights/trellis-python-sdk/commit/df550ea5095ac3c7cfc459c78b97c04ae8a4baa5))
* **internal:** codegen related update ([#86](https://github.com/Trellis-insights/trellis-python-sdk/issues/86)) ([9d55dd8](https://github.com/Trellis-insights/trellis-python-sdk/commit/9d55dd804c4418957011d146cc6918e58fb86709))
* **internal:** remove some duplicated imports ([#83](https://github.com/Trellis-insights/trellis-python-sdk/issues/83)) ([8de6623](https://github.com/Trellis-insights/trellis-python-sdk/commit/8de66234732f95e0704060d2637af9f3ac3a383d))
* **internal:** updated imports ([#84](https://github.com/Trellis-insights/trellis-python-sdk/issues/84)) ([75bd657](https://github.com/Trellis-insights/trellis-python-sdk/commit/75bd6572da9d85ecd331d891c2586139e181e3a9))

## 2.17.0 (2024-12-12)

Full Changelog: [v2.16.0...v2.17.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.16.0...v2.17.0)

### Features

* **api:** api update ([#72](https://github.com/Trellis-insights/trellis-python-sdk/issues/72)) ([46202a1](https://github.com/Trellis-insights/trellis-python-sdk/commit/46202a187184d9279c5352237ff50f08ee37e255))


### Chores

* **internal:** codegen related update ([#70](https://github.com/Trellis-insights/trellis-python-sdk/issues/70)) ([722651c](https://github.com/Trellis-insights/trellis-python-sdk/commit/722651c6c5a69edcfdb42413efa1f257c5d924f9))

## 2.16.0 (2024-12-09)

Full Changelog: [v2.15.0...v2.16.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.15.0...v2.16.0)

### Features

* **api:** api update ([#68](https://github.com/Trellis-insights/trellis-python-sdk/issues/68)) ([a6de665](https://github.com/Trellis-insights/trellis-python-sdk/commit/a6de66565f7c76c2bb1f47d40ff281ad9abb9f9a))


### Chores

* make the `Omit` type public ([#66](https://github.com/Trellis-insights/trellis-python-sdk/issues/66)) ([66fa221](https://github.com/Trellis-insights/trellis-python-sdk/commit/66fa221d0a2827d9cc8cb9ca04b5755505ba561a))

## 2.15.0 (2024-12-05)

Full Changelog: [v2.14.0...v2.15.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.14.0...v2.15.0)

### Features

* **api:** api update ([#63](https://github.com/Trellis-insights/trellis-python-sdk/issues/63)) ([790fbfe](https://github.com/Trellis-insights/trellis-python-sdk/commit/790fbfe7fa61ef7e758af4ae1d95db25c9ab5ee1))

## 2.14.0 (2024-12-04)

Full Changelog: [v2.13.0...v2.14.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.13.0...v2.14.0)

### Features

* **api:** api update ([#61](https://github.com/Trellis-insights/trellis-python-sdk/issues/61)) ([bf05d96](https://github.com/Trellis-insights/trellis-python-sdk/commit/bf05d96956c829cf59e1d038636da8f918a672e8))


### Chores

* **internal:** bump pyright ([#59](https://github.com/Trellis-insights/trellis-python-sdk/issues/59)) ([037d1ad](https://github.com/Trellis-insights/trellis-python-sdk/commit/037d1ade785e1bf8f2e3e166490cc1c8fafea389))

## 2.13.0 (2024-12-03)

Full Changelog: [v2.12.0...v2.13.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.12.0...v2.13.0)

### Features

* **api:** api update ([#56](https://github.com/Trellis-insights/trellis-python-sdk/issues/56)) ([624e1fb](https://github.com/Trellis-insights/trellis-python-sdk/commit/624e1fb6b4c1700763bd693e4a4c09efc0043375))

## 2.12.0 (2024-12-03)

Full Changelog: [v2.11.1...v2.12.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.11.1...v2.12.0)

### Features

* **api:** api update ([#53](https://github.com/Trellis-insights/trellis-python-sdk/issues/53)) ([099960c](https://github.com/Trellis-insights/trellis-python-sdk/commit/099960c513703f9ef4e07645c5bda29f59f1622d))

## 2.11.1 (2024-11-30)

Full Changelog: [v2.11.0...v2.11.1](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.11.0...v2.11.1)

### Bug Fixes

* **client:** compat with new httpx 0.28.0 release ([#50](https://github.com/Trellis-insights/trellis-python-sdk/issues/50)) ([58d5ff4](https://github.com/Trellis-insights/trellis-python-sdk/commit/58d5ff46fe2eac01eae08a159d5a3a6cf7c44d63))


### Chores

* **internal:** codegen related update ([#51](https://github.com/Trellis-insights/trellis-python-sdk/issues/51)) ([42b53d2](https://github.com/Trellis-insights/trellis-python-sdk/commit/42b53d25fd7ecdbea8d3448c876a160d23b48b7b))
* **internal:** exclude mypy from running on tests ([#49](https://github.com/Trellis-insights/trellis-python-sdk/issues/49)) ([25c6624](https://github.com/Trellis-insights/trellis-python-sdk/commit/25c66242d5e38467524170b65c4feb8fa3dadcf7))
* **internal:** fix compat model_dump method when warnings are passed ([#45](https://github.com/Trellis-insights/trellis-python-sdk/issues/45)) ([1414574](https://github.com/Trellis-insights/trellis-python-sdk/commit/141457421701d0e421b0f0a3d8ac9150812ca824))
* remove now unused `cached-property` dep ([#48](https://github.com/Trellis-insights/trellis-python-sdk/issues/48)) ([f5f0514](https://github.com/Trellis-insights/trellis-python-sdk/commit/f5f0514c7ca257734938d70bb95ba4bacc196445))


### Documentation

* add info log level to readme ([#47](https://github.com/Trellis-insights/trellis-python-sdk/issues/47)) ([f4d4098](https://github.com/Trellis-insights/trellis-python-sdk/commit/f4d40980ee537f17c5ffc4b64dc6c377204cee90))

## 2.11.0 (2024-11-22)

Full Changelog: [v2.10.0...v2.11.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.10.0...v2.11.0)

### Features

* **api:** api update ([#42](https://github.com/Trellis-insights/trellis-python-sdk/issues/42)) ([573894d](https://github.com/Trellis-insights/trellis-python-sdk/commit/573894d1c1c73c707e2266c6a62c77c93395864e))

## 2.10.0 (2024-11-21)

Full Changelog: [v2.9.0...v2.10.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.9.0...v2.10.0)

### Features

* **api:** api update ([#39](https://github.com/Trellis-insights/trellis-python-sdk/issues/39)) ([8339ef2](https://github.com/Trellis-insights/trellis-python-sdk/commit/8339ef2482e6717f9c637d2cb0f33577a62a124f))

## 2.9.0 (2024-11-20)

Full Changelog: [v2.8.0...v2.9.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.8.0...v2.9.0)

### Features

* **api:** api update ([#36](https://github.com/Trellis-insights/trellis-python-sdk/issues/36)) ([28bd739](https://github.com/Trellis-insights/trellis-python-sdk/commit/28bd739007f8abf80c585972688b070247089f4b))

## 2.8.0 (2024-11-19)

Full Changelog: [v2.7.0...v2.8.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.7.0...v2.8.0)

### Features

* **api:** api update ([#34](https://github.com/Trellis-insights/trellis-python-sdk/issues/34)) ([78e7e72](https://github.com/Trellis-insights/trellis-python-sdk/commit/78e7e7296a8dd92930c7686464038c4db3eb2e69))


### Chores

* rebuild project due to codegen change ([#31](https://github.com/Trellis-insights/trellis-python-sdk/issues/31)) ([8f4e063](https://github.com/Trellis-insights/trellis-python-sdk/commit/8f4e063760250eb837c5108c10fa008fb972cd36))
* rebuild project due to codegen change ([#33](https://github.com/Trellis-insights/trellis-python-sdk/issues/33)) ([f2741e6](https://github.com/Trellis-insights/trellis-python-sdk/commit/f2741e603647352259927f36690be8749ef95ad1))

## 2.7.0 (2024-11-15)

Full Changelog: [v2.6.0...v2.7.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.6.0...v2.7.0)

### Features

* **api:** api update ([#28](https://github.com/Trellis-insights/trellis-python-sdk/issues/28)) ([c9dd3eb](https://github.com/Trellis-insights/trellis-python-sdk/commit/c9dd3ebd388450811ce803cf2d50db12a953324c))

## 2.6.0 (2024-11-14)

Full Changelog: [v2.5.0...v2.6.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.5.0...v2.6.0)

### Features

* **api:** api update ([#25](https://github.com/Trellis-insights/trellis-python-sdk/issues/25)) ([5d2edd6](https://github.com/Trellis-insights/trellis-python-sdk/commit/5d2edd6542a79ba9869c85d4e5393c22dcef5b30))

## 2.5.0 (2024-11-12)

Full Changelog: [v2.4.0...v2.5.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.4.0...v2.5.0)

### Features

* **api:** api update ([#23](https://github.com/Trellis-insights/trellis-python-sdk/issues/23)) ([ff17ba8](https://github.com/Trellis-insights/trellis-python-sdk/commit/ff17ba891278e8a0b020dd96ec7779d72ead61c4))


### Chores

* rebuild project due to codegen change ([#21](https://github.com/Trellis-insights/trellis-python-sdk/issues/21)) ([d837a3c](https://github.com/Trellis-insights/trellis-python-sdk/commit/d837a3ccc1471ca619f97ee42f7014ee1711b8b0))

## 2.4.0 (2024-11-11)

Full Changelog: [v2.3.0...v2.4.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.3.0...v2.4.0)

### Features

* **api:** api update ([#18](https://github.com/Trellis-insights/trellis-python-sdk/issues/18)) ([bb5ab13](https://github.com/Trellis-insights/trellis-python-sdk/commit/bb5ab132cfc7f0576aa5ea0ed21e8e3bb622d684))

## 2.3.0 (2024-11-10)

Full Changelog: [v2.2.0...v2.3.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.2.0...v2.3.0)

### Features

* **api:** api update ([#15](https://github.com/Trellis-insights/trellis-python-sdk/issues/15)) ([6b673e1](https://github.com/Trellis-insights/trellis-python-sdk/commit/6b673e1a993e881471a55a5a16923a44b5bc9eae))

## 2.2.0 (2024-11-10)

Full Changelog: [v2.1.0...v2.2.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.1.0...v2.2.0)

### Features

* **api:** manual updates ([#12](https://github.com/Trellis-insights/trellis-python-sdk/issues/12)) ([f17a6d7](https://github.com/Trellis-insights/trellis-python-sdk/commit/f17a6d79b8e757344a6ddef9b5210837b7907e65))

## 2.1.0 (2024-11-10)

Full Changelog: [v2.0.0...v2.1.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v2.0.0...v2.1.0)

### Features

* **api:** api update ([#10](https://github.com/Trellis-insights/trellis-python-sdk/issues/10)) ([ebdfa0f](https://github.com/Trellis-insights/trellis-python-sdk/commit/ebdfa0fc9e6ca38ad74fa0f7a4cc09a6d0e5f824))
* **api:** api update ([#8](https://github.com/Trellis-insights/trellis-python-sdk/issues/8)) ([d7eadfc](https://github.com/Trellis-insights/trellis-python-sdk/commit/d7eadfcb12a6433ef6e2fd8e855d101ed0448a5f))

## 2.0.0 (2024-11-07)

Full Changelog: [v1.0.0...v2.0.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v1.0.0...v2.0.0)

### Chores

* update SDK settings ([#5](https://github.com/Trellis-insights/trellis-python-sdk/issues/5)) ([d244250](https://github.com/Trellis-insights/trellis-python-sdk/commit/d244250f38ee062e0885904076fd841ca27593f1))

## 1.0.0 (2024-11-04)

Full Changelog: [v0.0.1-alpha.0...v1.0.0](https://github.com/Trellis-insights/trellis-python-sdk/compare/v0.0.1-alpha.0...v1.0.0)

### Chores

* go live ([#1](https://github.com/Trellis-insights/trellis-python-sdk/issues/1)) ([15992d4](https://github.com/Trellis-insights/trellis-python-sdk/commit/15992d4245d6e4d1c8a82c18c854ffa74d8090c4))
* update SDK settings ([#3](https://github.com/Trellis-insights/trellis-python-sdk/issues/3)) ([161e906](https://github.com/Trellis-insights/trellis-python-sdk/commit/161e90633a5a1d70c5c8a87a507bbca521ecb2ba))
