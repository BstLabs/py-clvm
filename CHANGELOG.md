# Version v1.1.11

# Change Summary
- Added new command for installing `aws` cli #231 
- Fixed `clvm ssh new` fails on non-default profile #228 
- Fixed fails on Azure after changing password #229 

# Version: v1.1.11b

* [82086ec](https://github.com/BstLabs/py-clvm/commit/82086ec235025a7cdaeb2056c58c4b8c5a7c2503): Pre-Release PR v1.1.11b (#221)

* Make Azure operation faster due to using REST API (#213)

* Implement REST API in some functions

* Add list VMs via REST API

* Add some REST API operations

* Make RestApi class singleton

* Add token to cache

* Add token to cache exceptions

* Change running Azure tunnel

* Change wait for VM runtime to be ready

* Fix for "instance command" and "connect"

* Add multi-session mode on Azure

* Fix ssh call on Windows

* Refactor lint

* Stop VM after VSCode close

* Fix vscode call on Windows

* Refactor lint

* version bump v1.1.11b (pre-release)

Co-authored-by: Dmitry Slobodchikov <zoosman@mail.ru>


# Version: v1.1.10

* [2888655](https://github.com/BstLabs/py-clvm/commit/2888655d98afe7905f21b4a04592a50e1773baf8): Release PR v1.1.10 (#211)

* Docs: Changed changelog type to commit messages

* version bump v1.1.10 (stable)
* [98b8a05](https://github.com/BstLabs/py-clvm/commit/98b8a054ad5ed3d852c56f86aaec73d848faf9d4): [Changelog CI] Add Changelog for Version v1.1.10b (#210)
* [8077372](https://github.com/BstLabs/py-clvm/commit/80773727d2073c8dca7b47d2dbc2c3e93ef407ee): Docs(update): Modified and enhanced existing documentation (#209)

* Docs(update): Modified and enhanced docs

Description:
- Removed redundant checklist from PR template
- Applied new changelog workflow and config for it
- Added new indicator badges to README for:
	- PyPi version,
	- License,
	- Changelog,
	- Linter
	- Type checker

Co-authored-by: Dmitry Slobodchikov <zoosman@mail.ru>
* [f8f56b5](https://github.com/BstLabs/py-clvm/commit/f8f56b5611e9a3697e8e62f325cc7e961e7178c4): Update CHANGELOG.md
* [7cbd47c](https://github.com/BstLabs/py-clvm/commit/7cbd47ccba209cca9f8dfe0faedfa7403e41ff62): Docs(changelog): update release notes

# Version: v1.1.10b (beta version)

* Fixed(session): The stopped VM's failure on the first try to start a session. (#204)
* Fixed: Lost support for profile argument solved.
* Fixed(Azure): jdict codec serialization bug (#206)

Description:
- Added waiter for starting instance
- Modified the session start to wait until the VM is running

Co-authored-by: Dmitry Slobodchikov <zoosman@mail.ru>


**Full Changelog**: https://github.com/BstLabs/py-clvm/compare/v1.1.9...v1.1.10.b


## [v1.1.9](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.9) - 2022-10-12 15:41:38

### Feature
* Feat(config): Implemented the first version of `configure` for AWS by @orkhanshirin in https://github.com/BstLabs/py-clvm/pull/202


**Full Changelog**: https://github.com/BstLabs/py-clvm/compare/v1.1.8...v1.1.9

## [v1.1.8](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.8) - 2022-09-29 15:11:42

## [v1.1.8b1](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.8b1) - 2022-09-20 16:43:53

*No description*

## [v1.1.8b0](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.8b0) - 2022-09-11 05:35:45

Release PR v1.1.8b0 (patched) 

* Fixed bugs related to authk (https://github.com/BstLabs/py-authk). Authk fixed and released a new version 1.0.4b1
* Fidex minor bugs #181

Description:
Launching VM instances on GCP and Azure is more time-consuming now. It happens because of cloud platform machine's status is not the status of the runtime (operating system or particular dedicated application) running on the instance being ready. On GCP it takes approx. 60 sec., on Azure approx. 30 sec. To reduce this time, install the clvm queueing utility from https://github.com/BstLabs/py-clvm-utilities. This utility demands queueing permission on a specific cloud platform.

### Bug Fixes

- general:
  - Fix ssh new on AWS ([8c8a121](https://github.com/BstLabs/py-clvm/commit/8c8a121be1cdf1a4e4c6147156ed9ffdb4b8cef3)) ([#183](https://github.com/BstLabs/py-clvm/pull/183))
  - Fix requirements libs ([b83b95b](https://github.com/BstLabs/py-clvm/commit/b83b95be2395a22220959ef3f83f087678c15ab9)) ([#183](https://github.com/BstLabs/py-clvm/pull/183))
  - Fix platform recognition #181 ([ce5c98a](https://github.com/BstLabs/py-clvm/commit/ce5c98abf670fca85d23b6324317797436f2b468)) ([#183](https://github.com/BstLabs/py-clvm/pull/183))

## [v1.1.7b](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.7b) - 2022-09-05 14:59:21

*No description*

## [v1.1.7](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.7) - 2022-09-02 14:27:06

*No description*

### Bug Fixes

- general:
  - Fixed `clvm instance command` pwd (#176) ([238ec27](https://github.com/BstLabs/py-clvm/commit/238ec2728a39ba24c25c28a9de475206da6f9744)) ([#176](https://github.com/BstLabs/py-clvm/pull/176))
  - Fixed `clvm instance command -h` help messages (#174) ([18a6f77](https://github.com/BstLabs/py-clvm/commit/18a6f77f26bba378aa88c3eb7819dde39ea2ce90)) ([#174](https://github.com/BstLabs/py-clvm/pull/174))

### Bug Fixes

- general:
  - Fixed `clvm instance command` pwd (#176) ([238ec27](https://github.com/BstLabs/py-clvm/commit/238ec2728a39ba24c25c28a9de475206da6f9744)) ([#176](https://github.com/BstLabs/py-clvm/pull/176))
  - Fixed `clvm instance command -h` help messages (#174) ([18a6f77](https://github.com/BstLabs/py-clvm/commit/18a6f77f26bba378aa88c3eb7819dde39ea2ce90)) ([#174](https://github.com/BstLabs/py-clvm/pull/174))

## [v1.1.6](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.6) - 2022-08-19 15:19:54

Fix some minor bugs.
Add a waiting process for a VM to start based on Queue services (GCP, Azure).
Fix non-default profile ignorance on AWS. 

### Bug Fixes

- general:
  - Fix ssh new wait VM to be run on AWS ([76cf9f9](https://github.com/BstLabs/py-clvm/commit/76cf9f9063448e0dad8a933f9522f50de17af172)) ([#171](https://github.com/BstLabs/py-clvm/pull/171))
  - Fix non-default profile on AWS #115 ([c321dc1](https://github.com/BstLabs/py-clvm/commit/c321dc11bcddfcf04bcb7564e63637ca8925f50e)) ([#171](https://github.com/BstLabs/py-clvm/pull/171))
  - Fix exception no resource for GCP ([02af9f7](https://github.com/BstLabs/py-clvm/commit/02af9f7cd34138828de11cfda0da46fb24793e18)) ([#170](https://github.com/BstLabs/py-clvm/pull/170))
  - Fix ssh config mess ([8fa54d4](https://github.com/BstLabs/py-clvm/commit/8fa54d4de60aa00e4f08bc09fb228dcbdfca6ebf)) ([#169](https://github.com/BstLabs/py-clvm/pull/169))
  - Fix supress traceback on connect ([9b6cf94](https://github.com/BstLabs/py-clvm/commit/9b6cf944f9e33d65dad6c1228bead72be3e42c4a)) ([#165](https://github.com/BstLabs/py-clvm/pull/165))
  - Fix using cached credentials on Azure ([ff0fb9e](https://github.com/BstLabs/py-clvm/commit/ff0fb9ec209bde8f0d7f7a33b1583c4b3d6ce9f7)) ([#163](https://github.com/BstLabs/py-clvm/pull/163))

### Refactor

- general:
  - Refactor fix ([a2027d5](https://github.com/BstLabs/py-clvm/commit/a2027d5ffd147520cd0c027cf59987dd083aeff9)) ([#170](https://github.com/BstLabs/py-clvm/pull/170))
  - Refactor fix ([3c42815](https://github.com/BstLabs/py-clvm/commit/3c42815b2bc87697cc63f0711d780c499fca864c)) ([#170](https://github.com/BstLabs/py-clvm/pull/170))
  - Refactor fix ([aab4f16](https://github.com/BstLabs/py-clvm/commit/aab4f16b3946ad961b469a2209b3083f797ce5aa)) ([#169](https://github.com/BstLabs/py-clvm/pull/169))
  - Refactor fix ([4c4003b](https://github.com/BstLabs/py-clvm/commit/4c4003b67117bef0239aa65eb5d502b7e6d6e08b)) ([#165](https://github.com/BstLabs/py-clvm/pull/165))

## [v1.1.5](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.5) - 2022-08-10 14:44:13

*No description*

### Bug Fixes

- general:
  - Fix ssh new platform mess ([a3a9763](https://github.com/BstLabs/py-clvm/commit/a3a97631b844a7987092d947f5173bb3712547d9)) ([#160](https://github.com/BstLabs/py-clvm/pull/160))
  - Fix ssh clvm for Azure for Windows ([790bab5](https://github.com/BstLabs/py-clvm/commit/790bab5b3b37e443e6258adbe487722043b58931)) ([#158](https://github.com/BstLabs/py-clvm/pull/158))
  - Fix ssh for Azure for Windows ([875dcc2](https://github.com/BstLabs/py-clvm/commit/875dcc29ae928277e01f259589b3b33291bb1999)) ([#158](https://github.com/BstLabs/py-clvm/pull/158))
  - Fix ssh for GCP for Windows ([b4b0fe8](https://github.com/BstLabs/py-clvm/commit/b4b0fe8cfeecfe19ec010fc442b9e1df55795f28)) ([#158](https://github.com/BstLabs/py-clvm/pull/158))
  - Fix #153 vscode adjust ([2211c68](https://github.com/BstLabs/py-clvm/commit/2211c68fd106aa62e3d8c1fa13e3fe7957dd4745)) ([#155](https://github.com/BstLabs/py-clvm/pull/155))

### Refactor

- general:
  - Refactor fix ([1677611](https://github.com/BstLabs/py-clvm/commit/167761119926c6336ce996bcd91cae4d7cd4279a)) ([#160](https://github.com/BstLabs/py-clvm/pull/160))
  - Refactor fix ([c598a0f](https://github.com/BstLabs/py-clvm/commit/c598a0f909cec428129713bc03acd81bd173efff)) ([#158](https://github.com/BstLabs/py-clvm/pull/158))
  - Refactor fix ([b587e20](https://github.com/BstLabs/py-clvm/commit/b587e2080878eb8e0d65b8b6d4bfbf79238b2172)) ([#156](https://github.com/BstLabs/py-clvm/pull/156))
  - Refactor fix ([ba65720](https://github.com/BstLabs/py-clvm/commit/ba657204a803848198dd07c180aa5097cf6d8697)) ([#156](https://github.com/BstLabs/py-clvm/pull/156))
  - Refactor fix ([fe1c39e](https://github.com/BstLabs/py-clvm/commit/fe1c39eecfde65dbc6f0f2180ee73ba2cef4617e)) ([#155](https://github.com/BstLabs/py-clvm/pull/155))

## [v1.1.4](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.4) - 2022-08-08 14:57:49

Add GCP Default credentials tips. Fixed minors. 

## [v1.1.3](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.3) - 2022-08-08 13:33:12

*No description*

### Bug Fixes

- general:
  - Fix minors, add lib to pyproject.toml ([32e199a](https://github.com/BstLabs/py-clvm/commit/32e199a7a4e6620cf1a744b1fcd548dc51c3e4e3)) ([#143](https://github.com/BstLabs/py-clvm/pull/143))
  - Fix #144 "start before connect" ([9b114c5](https://github.com/BstLabs/py-clvm/commit/9b114c546a3816f5acbd663b32b2236a9e04edee)) ([#145](https://github.com/BstLabs/py-clvm/pull/145))
  - Fix GCP default credentials ([39944a4](https://github.com/BstLabs/py-clvm/commit/39944a4cf35c8baf78d68bc83c7218be7b8d8bf8)) ([#143](https://github.com/BstLabs/py-clvm/pull/143))

### Refactor

- general:
  - Refactor GCP config/ssh start ([2d5eb3f](https://github.com/BstLabs/py-clvm/commit/2d5eb3ff5c787f2bf09d4e19c1c36ffdb878bf37)) ([#147](https://github.com/BstLabs/py-clvm/pull/147))
  - Refactor minors ([58ca2b3](https://github.com/BstLabs/py-clvm/commit/58ca2b3cd3fb2867a98471e96fe7bc90ec2c85bd)) ([#145](https://github.com/BstLabs/py-clvm/pull/145))

## [v1.1.2](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.2) - 2022-07-28 08:28:08

*No description*

### Refactor

- general:
  - Refactored port mapping (#137) ([6edc689](https://github.com/BstLabs/py-clvm/commit/6edc6896f7162b697d5d6f5489c8106b49138e78)) ([#137](https://github.com/BstLabs/py-clvm/pull/137))

## [v1.1.1](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.1) - 2022-07-26 14:22:50

*No description*

## [v1.1.0](https://github.com/BstLabs/py-clvm/releases/tag/v1.1.0) - 2022-07-19 13:05:11

*No description*

## [v1.0.9](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.9) - 2022-07-18 07:14:16

Fixes https://github.com/BstLabs/py-clvm/issues/108
Fixes https://github.com/BstLabs/py-clvm/issues/100
Fixes https://github.com/BstLabs/py-clvm/issues/95
Fixes https://github.com/BstLabs/py-clvm/issues/97
Fixes https://github.com/BstLabs/py-clvm/issues/98

## [v1.0.8](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.8) - 2022-07-07 08:27:50

*No description*

## [v1.0.7](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.7) - 2022-06-23 08:06:24

Upgraded dependency versions

## [v1.0.6](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.6) - 2022-06-22 09:02:37

Fix issue #100 

### Bug Fixes

- general:
  - Fix isort issue ([088421d](https://github.com/BstLabs/py-clvm/commit/088421dd02943f38ae35a6d546ca80aa86988d4a)) ([#102](https://github.com/BstLabs/py-clvm/pull/102))
  - Fix lint issue ([c931dd7](https://github.com/BstLabs/py-clvm/commit/c931dd7805bf03d5a8f841d73a09e9fe5f4a9c4f)) ([#102](https://github.com/BstLabs/py-clvm/pull/102))
  - Fix sessions ([ba60dcc](https://github.com/BstLabs/py-clvm/commit/ba60dcca5c94fbb582b5d4645bbd17756c488aad)) ([#101](https://github.com/BstLabs/py-clvm/pull/101))
  - Fix ls ([9d7a2f9](https://github.com/BstLabs/py-clvm/commit/9d7a2f9aea317740e59b12d76695b4ea1a44c976)) ([#101](https://github.com/BstLabs/py-clvm/pull/101))

## [v1.0.5](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.5) - 2022-06-03 09:27:18

Fixed #43 

## [v1.0.4](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.4) - 2022-06-01 13:23:26

Description.

### Bug Fixes

- general:
  - Fixed wrong version number ([05b2121](https://github.com/BstLabs/py-clvm/commit/05b2121da20c7686d6f94e00b5dcfbd5d66fe3df))

### Bug Fixes

- general:
  - Fixed wrong version number ([05b2121](https://github.com/BstLabs/py-clvm/commit/05b2121da20c7686d6f94e00b5dcfbd5d66fe3df))

## [v1.0.3](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.3) - 2022-06-01 12:49:39

*No description*

### Bug Fixes

- general:
  - Fixed lint check errors ([09f888e](https://github.com/BstLabs/py-clvm/commit/09f888e9cd713fd99a4352ffc4aecda47086893f)) ([#93](https://github.com/BstLabs/py-clvm/pull/93))

### Bug Fixes

- general:
  - Fixed lint check errors ([09f888e](https://github.com/BstLabs/py-clvm/commit/09f888e9cd713fd99a4352ffc4aecda47086893f)) ([#93](https://github.com/BstLabs/py-clvm/pull/93))

### Performance Improvements

- general:
  - Performance gain achieved for the ls command after Ec2AllInstancesMapping (#91) ([2e8a546](https://github.com/BstLabs/py-clvm/commit/2e8a546cd4bfb736fb17fed35f800a9a86b147b6)) ([#91](https://github.com/BstLabs/py-clvm/pull/91))

## [v1.0.2](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.2) - 2022-05-19 08:02:56

Fixes #77 
Fixes #78 

### Bug Fixes

- general:
  - Fixed help message consistency issue. Changed all messages to lower case ([d2e2316](https://github.com/BstLabs/py-clvm/commit/d2e231673ed234a605d797a5d0338f3236af15ae)) ([#75](https://github.com/BstLabs/py-clvm/pull/75))

### Bug Fixes

- general:
  - Fixed help message consistency issue. Changed all messages to lower case ([d2e2316](https://github.com/BstLabs/py-clvm/commit/d2e231673ed234a605d797a5d0338f3236af15ae)) ([#75](https://github.com/BstLabs/py-clvm/pull/75))

## [v1.0.1](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.1) - 2022-05-03 09:12:20

Fixed #15 
Fixed #17 

## [v1.0.0](https://github.com/BstLabs/py-clvm/releases/tag/v1.0.0) - 2022-04-21 10:36:54

Initial Release

### Bug Fixes

- general:
  - Fix calling MFA's ARN ([a360bc3](https://github.com/BstLabs/py-clvm/commit/a360bc3b9db96c5ff76b8419a2b261e2e2ddc2f7)) ([#42](https://github.com/BstLabs/py-clvm/pull/42))
  - Fixing the merge conflict ([e791d94](https://github.com/BstLabs/py-clvm/commit/e791d944957a5fb5054cc2b76d316bd0a3187402)) ([#26](https://github.com/BstLabs/py-clvm/pull/26))

\* *This CHANGELOG was automatically generated by [auto-generate-changelog](https://github.com/BobAnkh/auto-generate-changelog)*
