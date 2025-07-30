# Changelog

## 0.5.2 (2025-06-30)

Full Changelog: [v0.5.1...v0.5.2](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.5.1...v0.5.2)

### Bug Fixes

* **ci:** correct conditional ([94c312e](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/94c312ef54bc1b69c4cf67e9db1ab96303f71050))


### Chores

* **ci:** only run for pushes and fork pull requests ([48af9e4](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/48af9e4c8f546e89bfeaa3ae53e3f134429d44c6))

## 0.5.1 (2025-06-27)

Full Changelog: [v0.5.0...v0.5.1](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.5.0...v0.5.1)

### Bug Fixes

* **ci:** release-doctor — report correct token name ([7b270a8](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/7b270a8434d780262408f9003258a7177b4325bd))


### Chores

* **tests:** skip some failing tests on the latest python versions ([72e6a0f](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/72e6a0f2c994e06432dbc73cd88ee833bdcd32f8))

## 0.5.0 (2025-06-21)

Full Changelog: [v0.4.5...v0.5.0](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.4.5...v0.5.0)

### Features

* **client:** add follow_redirects request option ([ec8211d](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/ec8211d4e09a53565928fcf5c857f3c6c3bdf232))
* **client:** add support for aiohttp ([04b036f](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/04b036f10027fbc68afd2e3da4cc90d15b462b70))


### Bug Fixes

* **client:** correctly parse binary response | stream ([3b5553a](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/3b5553a71762a5035f99390b73db5fe4bc9a1004))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([e8598e8](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/e8598e8796a7da5e8cf516e7e13ee9e45bb743f7))


### Chores

* **ci:** enable for pull requests ([ac27a9f](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/ac27a9f381e616971683e8e4ceef381bdc205c0a))
* **ci:** fix installation instructions ([dc296a6](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/dc296a60f24bc49e4b96cfe80da6516b57c86fb6))
* **ci:** upload sdks to package manager ([6b05e3f](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/6b05e3fffe455471b54d0eee0fbe0133899e38d8))
* **docs:** grammar improvements ([4e230b0](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/4e230b096a391777f32ed3c3a68a2a7ea49a92e6))
* **docs:** remove reference to rye shell ([39bb2e8](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/39bb2e8bf70d0c9d85b8a97a5c0a2e3184f1cb45))
* **internal:** update conftest.py ([918f2bc](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/918f2bc12d2ea2bb9b65f1a5983c55fd5fcba4db))
* **readme:** update badges ([58c9d9f](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/58c9d9fbefe0959c59cfb53a96cf0a72e05c6d63))
* **tests:** add tests for httpx client instantiation & proxies ([dc4d424](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/dc4d4240e00459204702f333294affdf4664b58e))
* **tests:** run tests in parallel ([4ea4dce](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/4ea4dcec7acb10ed07f61632f63d0f4825519f50))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([b95c8a2](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/b95c8a2dcc501d91cd3c4d982519bacf9860f17b))

## 0.4.5 (2025-05-10)

Full Changelog: [v0.4.4...v0.4.5](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.4.4...v0.4.5)

### Bug Fixes

* **package:** support direct resource imports ([1bbe38b](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/1bbe38bccdaf96cb93f05156dfad63327fb75251))


### Chores

* broadly detect json family of content-type headers ([9696f85](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/9696f854bd8a11d3a9f4588b705a14df241eee7d))
* **ci:** only use depot for staging repos ([8366c18](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/8366c18776e9721d11e1ed59da191cd671a57ad2))
* **internal:** avoid errors for isinstance checks on proxies ([f1d85c9](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/f1d85c9bca13aeb16c4ac555d11082f61f4e1d39))
* **internal:** codegen related update ([6a0775b](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/6a0775b1b7c926d86021190093c55013339a758e))

## 0.4.4 (2025-04-23)

Full Changelog: [v0.4.3...v0.4.4](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.4.3...v0.4.4)

### Bug Fixes

* **pydantic v1:** more robust ModelField.annotation check ([134dc34](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/134dc346e742959c0862d76913484a8e83fd475a))


### Chores

* **ci:** add timeout thresholds for CI jobs ([7b209c7](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/7b209c7c095ac13a523f018bedc33acfd9f82eac))
* **client:** minor internal fixes ([3b928b8](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/3b928b8471e7fc7f6b078f14906b50baae8c72b9))
* **internal:** base client updates ([303d2c4](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/303d2c410aeeade045f418c132ab4c47d7890a78))
* **internal:** bump pyright version ([874a513](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/874a5136c47b658ada9f86a9d02c6e0975f12dda))
* **internal:** fix list file params ([0a36840](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/0a36840b106d34bb029117fa616bb4ef48c95968))
* **internal:** import reformatting ([2df74b7](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/2df74b77278e7b491302414ac1eb3f5267142bfc))
* **internal:** refactor retries to not use recursion ([647bf81](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/647bf8133a97063e476f68fff62ea155079700e5))
* **internal:** update models test ([9cdad1e](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/9cdad1e769938c8c1b79ff125a9e21753dcfeb87))
* **internal:** update pyright settings ([9dbfd29](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/9dbfd2979a94fc15374126e2c260693c0051b402))

## 0.4.3 (2025-04-12)

Full Changelog: [v0.4.2...v0.4.3](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.4.2...v0.4.3)

### Bug Fixes

* **perf:** optimize some hot paths ([d5c8b40](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/d5c8b40176f2c0dcf2fce6e13c2cc8f9ff537c10))
* **perf:** skip traversing types for NotGiven values ([58298e8](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/58298e8109368628361d526738bb8ac8da3816bf))


### Chores

* fix typos ([#45](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/45)) ([b74d775](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/b74d775eb684311f53511bc691706d81eaf1187f))
* **internal:** expand CI branch coverage ([edbf9a3](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/edbf9a301ea1bf763b36e2795e2ff049ef4f5787))
* **internal:** reduce CI branch coverage ([8bfea92](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/8bfea923cde8aab2da952b8517b6da03382e033d))
* **internal:** remove trailing character ([#47](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/47)) ([db29575](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/db29575f35df93a4211a5d9402cea30deefb9d10))
* **internal:** slight transform perf improvement ([#48](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/48)) ([a7588e8](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/a7588e870f2e867e1464bf3a54c010f5e98c5866))

## 0.4.2 (2025-03-17)

Full Changelog: [v0.4.1...v0.4.2](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.4.1...v0.4.2)

### Bug Fixes

* **ci:** ensure pip is always available ([#41](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/41)) ([06cf89d](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/06cf89d546387a5b227f82b58de6caac8ea1e3dd))
* **ci:** remove publishing patch ([#43](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/43)) ([cf0fc63](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/cf0fc63a80126a20a17d0f573148fd44949ad9bc))

## 0.4.1 (2025-03-15)

Full Changelog: [v0.4.0...v0.4.1](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.4.0...v0.4.1)

### Bug Fixes

* **types:** handle more discriminated union shapes ([#39](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/39)) ([55a22b3](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/55a22b3d9628535a44fee23889a65cae9fc50674))


### Chores

* **docs:** update client docstring ([#33](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/33)) ([7899368](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/7899368ef9cc1759e24b4d31e024542ab9db881a))
* **internal:** bump rye to 0.44.0 ([#38](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/38)) ([902a781](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/902a7811a1e08e61956ddced70a7a4f1bf407bce))
* **internal:** codegen related update ([#37](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/37)) ([6adca0f](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/6adca0f856aa41ec4239eceb7d3b5e956ce9b943))
* **internal:** properly set __pydantic_private__ ([#30](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/30)) ([c64d1fb](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/c64d1fb8d4b3db9e50b08df773c49884e3d1877f))
* **internal:** remove extra empty newlines ([#36](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/36)) ([41854fd](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/41854fdbf818cb41c8ab2e0162106f1d00aaa2e5))
* **internal:** remove unused http client options forwarding ([#34](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/34)) ([583c45b](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/583c45b5c68303a9a09158192522c3fe5ae5886c))


### Documentation

* update URLs from stainlessapi.com to stainless.com ([#32](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/32)) ([559ddde](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/559dddefe42ba19e1b6aa4e333fc5cd4cf6bf322))

## 0.4.0 (2025-02-24)

Full Changelog: [v0.3.0...v0.4.0](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.3.0...v0.4.0)

### Features

* **api:** api update ([#28](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/28)) ([7809e79](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/7809e79ba55bb3b75c53cdc17b2f7ab40a364a7f))


### Chores

* **internal:** fix devcontainers setup ([#26](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/26)) ([5937580](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/5937580009ce2f08dc851e1303aaac678abbe9e6))

## 0.3.0 (2025-02-21)

Full Changelog: [v0.2.0...v0.3.0](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.2.0...v0.3.0)

### Features

* **client:** allow passing `NotGiven` for body ([#23](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/23)) ([5206aea](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/5206aea5288d86d1165e1cf2be1e0c5b04437f60))


### Bug Fixes

* **client:** mark some request bodies as optional ([5206aea](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/5206aea5288d86d1165e1cf2be1e0c5b04437f60))

## 0.2.0 (2025-02-14)

Full Changelog: [v0.1.1...v0.2.0](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.1.1...v0.2.0)

### Features

* **client:** send `X-Stainless-Read-Timeout` header ([#18](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/18)) ([7390988](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/73909887d03bc31ab1de57a5bed8ff17fe2ebcaf))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#21](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/21)) ([a23a73c](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/a23a73cbf896b5b67f8205b65d93ea8d126ec580))


### Chores

* **internal:** bummp ruff dependency ([#17](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/17)) ([aaf96ed](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/aaf96ed10e589e8c7ce9abaf901b0a81a7274778))
* **internal:** change default timeout to an int ([#16](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/16)) ([feddf16](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/feddf163d12fe0ae96c0fa8d23b0b7534f5a6bf1))
* **internal:** fix type traversing dictionary params ([#19](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/19)) ([acd93c0](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/acd93c090fc7678a6410f98a27ecc55e3221453e))
* **internal:** minor formatting changes ([#14](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/14)) ([eaa08a9](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/eaa08a939ebf374ea8961b21745601d0fdcaf679))

## 0.1.1 (2025-01-22)

Full Changelog: [v0.1.0...v0.1.1](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.1.0...v0.1.1)

### Bug Fixes

* **tests:** make test_get_platform less flaky ([#10](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/10)) ([b57a3f5](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/b57a3f5d8a3e85653fe62ae8b97ff4d2135dc54e))


### Chores

* **internal:** avoid pytest-asyncio deprecation warning ([#11](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/11)) ([cf8f570](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/cf8f5703d338c7d8cbfaba7817170f8227ce9b00))
* **internal:** codegen related update ([#12](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/12)) ([767bb89](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/767bb89ece9430cfe0d46f03c14e2a85092f4b0a))
* **internal:** codegen related update ([#7](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/7)) ([1f84d5d](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/1f84d5dcd5b094379bacca0d2ad5b42a3e12ec1c))


### Documentation

* **raw responses:** fix duplicate `the` ([#9](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/9)) ([41a75d9](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/41a75d9f2b4fa2ad20eb86786aab623079aecab3))

## 0.1.0 (2025-01-10)

Full Changelog: [v0.0.1...v0.1.0](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.0.1...v0.1.0)

### Features

* **api:** update via SDK Studio ([#4](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/4)) ([f4fed85](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/f4fed85f8573cbd8deabb6df3d31b8329e9f8937))

## 0.0.1 (2025-01-10)

Full Changelog: [v0.0.1-alpha.0...v0.0.1](https://github.com/SigmaEf5ect/sigma-sdk-python/compare/v0.0.1-alpha.0...v0.0.1)

### Chores

* go live ([bf4c93b](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/bf4c93b2d494b045ee12abbef4c4b41352273113))
* update SDK settings ([#2](https://github.com/SigmaEf5ect/sigma-sdk-python/issues/2)) ([ffef085](https://github.com/SigmaEf5ect/sigma-sdk-python/commit/ffef0859dcb7380acb7ede0c418816cd7166a10c))
