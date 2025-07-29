# CHANGELOG


## v0.26.0 (2025-06-26)

### Build System

- Add H4H docs pages and some theme and extensions stuff
  ([`0771446`](https://github.com/bhklab/damply/commit/0771446e60fec8afed34634dca206624570bf04d))

- Update damply
  ([`2feac96`](https://github.com/bhklab/damply/commit/2feac96c36bf03ba37ab060eaf07299c75000984))

### Documentation

- Add page on group permission querying functions
  ([`6c99707`](https://github.com/bhklab/damply/commit/6c997078b4f266556da7e901150f5ffa9f982398))

### Features

- Add instructions for running audits on H4H
  ([`7c51cb0`](https://github.com/bhklab/damply/commit/7c51cb0b436d90b67981f7ed4acea4d7730dbc4f))


## v0.25.0 (2025-06-23)

### Chores

- Update lockfile
  ([`5e51e82`](https://github.com/bhklab/damply/commit/5e51e82467c9313ef55b33d15e920c6b8cabd828))

### Features

- Update ci
  ([`c1e3248`](https://github.com/bhklab/damply/commit/c1e3248d9f656da34a9a05da7a003a86b7348433))

- Update ci
  ([`8e82a4c`](https://github.com/bhklab/damply/commit/8e82a4c8d96bb030ccb04550f74d766131ef095d))


## v0.24.0 (2025-06-23)

### Bug Fixes

- Lint
  ([`747eed0`](https://github.com/bhklab/damply/commit/747eed0a7276dbf43279d9e95e87c974b693bc30))

- Only cache invalidate on major version upgrade
  ([`533469b`](https://github.com/bhklab/damply/commit/533469bc768f5aa72df14db658ea7ba80a8b3df0))

- Update sbatch to use DEBUG logging
  ([`6adbe63`](https://github.com/bhklab/damply/commit/6adbe63dc2df3be79d1a768dcc6ac34e31755948))

### Chores

- Format and lint
  ([`575e099`](https://github.com/bhklab/damply/commit/575e099542ba0e8a2c26ddebc55d3be656bdab43))

### Features

- Add ability to specify job time when running full-audit
  ([`c2dc630`](https://github.com/bhklab/damply/commit/c2dc63058e4a779082bdaafe8f2824f378535d2d))

- Functioning collect-audit and plot
  ([`9ad2749`](https://github.com/bhklab/damply/commit/9ad2749764ca77a690104f8ab6190e04a501ff7c))


## v0.23.1 (2025-06-23)

### Bug Fixes

- Update size_gb calculation to use ByteSize helper for better precision
  ([`aac73fb`](https://github.com/bhklab/damply/commit/aac73fb4e223eda9d0f2f792f0c4327c8fcc4dac))

### Chores

- Add plotly and kaleido dependencies for enhanced plotting capabilities
  ([`558b173`](https://github.com/bhklab/damply/commit/558b173a08bcc4f809e21a514d2e3cdcd1d720a0))

- Reintroduced plotly dependency with version constraints. - Added kaleido for static image
  generation in plots.

- Add plotly dependency
  ([`0e98480`](https://github.com/bhklab/damply/commit/0e984808cd963bb0793b3bf00efe3e2bcb09da7d))

- Setup plot module
  ([`2b33cf5`](https://github.com/bhklab/damply/commit/2b33cf5d027a5482265263de65795209cd464307))


## v0.23.0 (2025-06-20)

### Bug Fixes

- Add force option to project cli
  ([`05c4d84`](https://github.com/bhklab/damply/commit/05c4d849736a2a9873fbb7d05fb645d29ec74ae1))

### Chores

- Format and lint
  ([`1f99f38`](https://github.com/bhklab/damply/commit/1f99f3856587fca1284698b679ade8e95c934b01))

- Format and lint
  ([`3afc6af`](https://github.com/bhklab/damply/commit/3afc6aff16e243d850ee4dde9506c5a690d07cf9))

### Features

- Add collect_audits
  ([`584e989`](https://github.com/bhklab/damply/commit/584e989a60af0a059127cf0be1f804d033930764))

- Add collect_audits to cli
  ([`fabeb53`](https://github.com/bhklab/damply/commit/fabeb53cc41c260d2c204ec42113e5f35ca42461))


## v0.22.0 (2025-06-20)

### Chores

- Format
  ([`1bff79f`](https://github.com/bhklab/damply/commit/1bff79f00170db59100a555822feb40a4fe0fd18))

### Features

- Audit submission across both projects groups
  ([`d6590b3`](https://github.com/bhklab/damply/commit/d6590b30f759224cadb1c48fd4404b5d109fe8d9))


## v0.21.0 (2025-06-20)

### Features

- Ensure working audit
  ([`b61cbf4`](https://github.com/bhklab/damply/commit/b61cbf4fc4095e4bc05334876f8d3195400d5812))

- Started audit
  ([`58511e4`](https://github.com/bhklab/damply/commit/58511e409492b33568723ca25fe19e6346bf0f8f))


## v0.20.0 (2025-06-20)

### Chores

- Rearrange
  ([`c489eb5`](https://github.com/bhklab/damply/commit/c489eb5101b81ecd95ef060fa2109d87f430fcb0))

- Update module imports
  ([`797cd12`](https://github.com/bhklab/damply/commit/797cd1203cb66381e3aa5fcf7071ed773c5b59c1))

### Features

- Add find readme utilitiy
  ([`bbd4fd6`](https://github.com/bhklab/damply/commit/bbd4fd66c8cf3c573f89523a4cf8ed5b0759a369))

- Add find readme utilitiy to project and update cli to not show compuuted details
  ([`bd6e1eb`](https://github.com/bhklab/damply/commit/bd6e1eb5c3b67de9cd21652edbf14a47e0d2389c))


## v0.19.0 (2025-06-20)

### Bug Fixes

- Limit suffixes to 3 parts
  ([`2432717`](https://github.com/bhklab/damply/commit/2432717b6f69378c1581196f7c9780d80c9c4d49))

### Chores

- Add packaging
  ([`485fba7`](https://github.com/bhklab/damply/commit/485fba723b74db4053933613708b5dac79279e32))

### Features

- Validate against package version
  ([`53259a6`](https://github.com/bhklab/damply/commit/53259a64ecd6bb67b937e973ec6cfbb82a45669e))


## v0.18.2 (2025-06-19)

### Bug Fixes

- Better handling of cache
  ([`3b9c3bb`](https://github.com/bhklab/damply/commit/3b9c3bbde8f50721c31ba22789a11f9e3de089cc))

- Wrong mmethod
  ([`bd6d08c`](https://github.com/bhklab/damply/commit/bd6d08c304fcd569ed9c31944262aa25334e045b))

### Chores

- Update lockfile
  ([`2d0fefb`](https://github.com/bhklab/damply/commit/2d0fefb6296286bdb96bc2b5542f463e05769d02))


## v0.18.1 (2025-06-19)

### Bug Fixes

- Numbers arent suffixes
  ([`3076b4f`](https://github.com/bhklab/damply/commit/3076b4fb3d8a979adaaf1d9b93d9131460c09647))


## v0.18.0 (2025-06-19)

### Bug Fixes

- Remove last accessed, useless info
  ([`22f9d52`](https://github.com/bhklab/damply/commit/22f9d52d7b70d38f6166049450b9508ac2bb98e8))

### Chores

- Update lockfile
  ([`7d2b43f`](https://github.com/bhklab/damply/commit/7d2b43fd4fca7e0602147893a803d915142dfac4))

### Features

- Add file types and fix caching
  ([`6514bf6`](https://github.com/bhklab/damply/commit/6514bf63188e93e096d70582d64e02bc24a5c18b))

- Update default groups and refactor table building
  ([`764d012`](https://github.com/bhklab/damply/commit/764d0121300df94ea1962aff5d563db334d42885))


## v0.17.0 (2025-06-13)

### Chores

- Merge
  ([`3a7017b`](https://github.com/bhklab/damply/commit/3a7017b2e778998f526be65cca608e65cbbcbb71))

- Update lockfile
  ([`b78ce26`](https://github.com/bhklab/damply/commit/b78ce267eb47316f95e369d075970633fc645f3c))


## v0.16.0 (2025-06-13)

### Bug Fixes

- Merge
  ([`f91b94a`](https://github.com/bhklab/damply/commit/f91b94a7c8f55ae6d038c8d1b4c8ea2bc26f858b))

### Chores

- Fix ruff lint
  ([`573fb38`](https://github.com/bhklab/damply/commit/573fb38a6de6572d7ed5267ac4d9be729d0165e5))

- Ruff format
  ([`05d0b18`](https://github.com/bhklab/damply/commit/05d0b18ef680b0bf44a11a9b3dd466a81ef91a3e))

- Ruff format
  ([`93d71b2`](https://github.com/bhklab/damply/commit/93d71b2a7ffd93dbf09b2c9dc7d79d15a49267d0))

- Ruff format
  ([`957ebc6`](https://github.com/bhklab/damply/commit/957ebc6e3291e03729367b9601a2a750f9561158))

- Ruff lint
  ([`3886c94`](https://github.com/bhklab/damply/commit/3886c94604834e95c082c8a54e3b1e72003c8c92))

- Ruff lint
  ([`77bf13a`](https://github.com/bhklab/damply/commit/77bf13a620af4ce61b03ee52da8013323793ea35))

- Update lockfile
  ([`8946fd8`](https://github.com/bhklab/damply/commit/8946fd8659eba2814a91a18f75340893103de669))

### Continuous Integration

- Fix actions workflow
  ([`b01bbcb`](https://github.com/bhklab/damply/commit/b01bbcb97f6a8015ef36d2a4252c6aeb8d2a208a))

### Features

- Add file count and est time zone
  ([`dda9e24`](https://github.com/bhklab/damply/commit/dda9e24be2019ecd6ffa95edf2dbfdce1a9a9d25))

- Add platformdis
  ([`52610ef`](https://github.com/bhklab/damply/commit/52610efbda31dc580a5d3c4b87bebc6c7a0458b2))

- Setup cache dir
  ([`bf189a0`](https://github.com/bhklab/damply/commit/bf189a0e98585d2223bf12bb31f5fcf04a03bd8e))

- Setup directory audit to use user cache
  ([`08e18bf`](https://github.com/bhklab/damply/commit/08e18bf54771d2c8744e8cabf590ef78b12926b5))

- Validate
  ([`7674759`](https://github.com/bhklab/damply/commit/7674759fc4c3d8785d5e3e97dd88cc107544538c))


## v0.15.0 (2025-06-13)

### Chores

- Address ruff lint error
  ([`2782080`](https://github.com/bhklab/damply/commit/278208060c7f402a8f5d2895e25e5961c92f837e))

- Fix import order
  ([`6e4d44b`](https://github.com/bhklab/damply/commit/6e4d44b4ea149984704b2ca96663ed9c96fa9347))

- Ruff format
  ([`d686334`](https://github.com/bhklab/damply/commit/d686334a9b1a1221c499e4262962bb2b420c8e38))

- Ruff lint fix
  ([`0b3d627`](https://github.com/bhklab/damply/commit/0b3d627ce00dc3b9f8e332ba12bb76ebcfcdc05c))

- Suppress ruff lint
  ([`f203986`](https://github.com/bhklab/damply/commit/f2039867b7d19c7dd08232f6269ee25d66785aac))

### Features

- Cleanup deps
  ([`d7cc3c3`](https://github.com/bhklab/damply/commit/d7cc3c3443551077e0e4f3abb56015bc3f756e82))

- Update deps and style env
  ([`28954d4`](https://github.com/bhklab/damply/commit/28954d4c255144a114f41496fb184142beb6882d))


## v0.14.0 (2025-06-13)

### Chores

- Downgrade click version
  ([`e63ee31`](https://github.com/bhklab/damply/commit/e63ee3118c6089901ba1b8112ce9b9df62abb23a))

### Features

- Add click dependency
  ([`5fe9362`](https://github.com/bhklab/damply/commit/5fe93629c8a8a12b4df97bfe58366563df19e5f6))


## v0.13.0 (2025-06-13)

### Chores

- Deprecate old metadata
  ([`b5349e5`](https://github.com/bhklab/damply/commit/b5349e56e6c56a3b3a1efdc947fe2b007b20517e))

- Deprecate old whose
  ([`9a82ea1`](https://github.com/bhklab/damply/commit/9a82ea1c6bd3646501dce7c4e9074e3861370622))

### Documentation

- Update README
  ([`96a844e`](https://github.com/bhklab/damply/commit/96a844eef3a48623b267fb70a5d1597f97615f5b))

### Features

- Add whose cli entry point
  ([`bcbe058`](https://github.com/bhklab/damply/commit/bcbe058d54b7dbe9474f4345018835513a883159))


## v0.12.0 (2025-06-13)

### Bug Fixes

- Add command and close docstring
  ([`c315c13`](https://github.com/bhklab/damply/commit/c315c136c50a753044e4938af0e4cfe54dc0be12))

- Cli main error
  ([`aa0e319`](https://github.com/bhklab/damply/commit/aa0e319ca627683b1cc82569a5ddacaeb74b58af))

fix: add command and close docstring

### Chores

- Cleanup
  ([`80e6016`](https://github.com/bhklab/damply/commit/80e6016097385cfd3b0cec36a535da71e9b0b677))

- Fix tests
  ([`3aa876a`](https://github.com/bhklab/damply/commit/3aa876aa081ad3d864c37aa2cf1abefa9d6ba055))

- Update deps
  ([`dd11ff0`](https://github.com/bhklab/damply/commit/dd11ff0db645f789256f03863068e1549969c86b))

- Update lockfile
  ([`9efa8be`](https://github.com/bhklab/damply/commit/9efa8beab9063c3b5d6b6d91312d8d8fbde25793))

### Features

- Add logging config
  ([`06f2a33`](https://github.com/bhklab/damply/commit/06f2a3324172ad6c57bdf063ae19df0e425c3870))

- Full refactor
  ([`b8811c3`](https://github.com/bhklab/damply/commit/b8811c3001605bd0278e58eab87179966e220843))

- Full refactor
  ([`b305597`](https://github.com/bhklab/damply/commit/b3055973636327d5a16648bf63d95e94245ef0ea))

feat: full refactor, simplifying CLI

- Refactor to work
  ([`b71c9cf`](https://github.com/bhklab/damply/commit/b71c9cf486ad860b2ac0899da3fdace6dc0e8773))

- Small fix
  ([`5459162`](https://github.com/bhklab/damply/commit/5459162bf5eef85df916bf696a4c60a66ba9d033))

- Update directory_list mod
  ([`6038756`](https://github.com/bhklab/damply/commit/60387569ea4750863bc0802d2b7047544456fa69))

### Refactoring

- Cleanup
  ([`0aa11ee`](https://github.com/bhklab/damply/commit/0aa11eef476f90df9de47794c7467b854391d8f2))


## v0.11.0 (2025-05-26)

### Bug Fixes

- Add custom exception for unset environment variables
  ([`784080a`](https://github.com/bhklab/damply/commit/784080a42b927e6f9dc5bf94b1e940ddc283e045))

- Adjust test for Windows path handling to set strict mode explicitly
  ([`57db00a`](https://github.com/bhklab/damply/commit/57db00a24484b857a5d7674942c587a4e34c75af))

- Restore assertion for Windows file owner retrieval test
  ([`9986a79`](https://github.com/bhklab/damply/commit/9986a7989e061c108d4e09d55de779753871ffba))

- Update sha256 checksum for damply package version 0.10.0
  ([`0be6951`](https://github.com/bhklab/damply/commit/0be695117bbe86d476753edc2a7cde339a29faba))

### Chores

- Update version and checksum in pixi.lock; modify README metadata
  ([`b480d2b`](https://github.com/bhklab/damply/commit/b480d2babb75c0226e00dc8174a3fdc86f0a77b1))

### Documentation

- Clean up index.md
  ([`3b1d489`](https://github.com/bhklab/damply/commit/3b1d489aa0f41e12f083f826c9d041e451a0541c))

- Remove about page
  ([`c960dbd`](https://github.com/bhklab/damply/commit/c960dbdd9211c08b56d8cea175d6332bf3457200))

- Update to mkdocs
  ([`6f8c456`](https://github.com/bhklab/damply/commit/6f8c456f49917d8fe8233ee3ede81f03fc40d308))

### Features

- Add documentation for DamplyDirs module and its usage
  ([`74d9c79`](https://github.com/bhklab/damply/commit/74d9c7987d8bdf8affbdef12b6985c8382432b0a))

- Add Windows support to CI workflow matrix
  ([`650c192`](https://github.com/bhklab/damply/commit/650c19286021844586937c3d11ecb2b916f82c48))

- Implement DamplyDirs singleton initialization and add comprehensive tests
  ([`c48deb9`](https://github.com/bhklab/damply/commit/c48deb97837259542950c1ab6d31831ee911c31a))

- Refactor damplydirs logic, include documentation, and add comprehensive tests
  ([`cf026d4`](https://github.com/bhklab/damply/commit/cf026d4ff0351af3cc109e2d802ddc14c9b1c78e))

feat: refactor damplydirs logic, include documentation, and add comprehensive tests

### Refactoring

- Streamline directory structure handling and improve error management
  ([`00ad73d`](https://github.com/bhklab/damply/commit/00ad73dd79d364b7950410c39898c39c04aebd42))

- Update file owner tests for platform-specific handling and improve readability
  ([`860d04f`](https://github.com/bhklab/damply/commit/860d04fb8d1a30928c08e7633b494d1be3f7087c))


## v0.10.0 (2025-05-20)

### Bug Fixes

- Update pypi references from '.' to './' for consistency
  ([`bc1715f`](https://github.com/bhklab/damply/commit/bc1715f7b692b5ea8f6ab239df1c698c7e419f0d))

- Update repository references and descriptions from jjjermiah to bhklab
  ([`ad73779`](https://github.com/bhklab/damply/commit/ad73779b06649b2e1f173eea26f2d508b871ab15))

### Chores

- Comment out Test-PyPi-Installation and Publish-To-Test-PyPi jobs in CI workflow
  ([`2ed0229`](https://github.com/bhklab/damply/commit/2ed0229f43e0b0a3b46cf52a77478840afcf305b))

- Format and lint
  ([`5130657`](https://github.com/bhklab/damply/commit/5130657f3fd937dd4e0ea15079df9e1473adeac6))

- Move ruff config out and update deps
  ([`2f5a3fe`](https://github.com/bhklab/damply/commit/2f5a3fe4defebcb19bfcf7abc0643ce405787523))

- Reformat
  ([`7a275c7`](https://github.com/bhklab/damply/commit/7a275c772c8d86f8223c746625fc35f621fc4f05))

- Remove empty __init__.py file from dmpdirs directory
  ([`47ff2cd`](https://github.com/bhklab/damply/commit/47ff2cd9916039b8397fd02141d8a1a422a657b6))

- Update lockfile
  ([`aa9e4d9`](https://github.com/bhklab/damply/commit/aa9e4d93ceeaed09c559f2e71ff9e7af8a9675da))

### Code Style

- Standardize indentation and formatting in whose.py
  ([`07e495f`](https://github.com/bhklab/damply/commit/07e495f9a54c366abee030a832e7f92662a6e073))

### Continuous Integration

- Disable fail-fast in job strategy for improved stability across OS matrix
  ([`f84c26e`](https://github.com/bhklab/damply/commit/f84c26e43579614623633649967e5aa310adf0bf))

- Streamline Codecov integration by removing redundant steps and ensuring coverage tracking
  ([`eb1fdef`](https://github.com/bhklab/damply/commit/eb1fdef4fa4f776d0c5d26a243863dd23fa02831))

- Update actions versions
  ([`5e341a8`](https://github.com/bhklab/damply/commit/5e341a83e909251f756d33eebf4d16b59759aa24))

### Features

- Add dmpdirs module for standardized project directory access
  ([`dc324e6`](https://github.com/bhklab/damply/commit/dc324e612f72d4cde802377dd9ae98d421705afd))

- Add dmpdirs module for standardized project directory access
  ([`0eeb8c5`](https://github.com/bhklab/damply/commit/0eeb8c58a35ae3b81c41a843567092acc76931f5))

- Update dependencies and refactor codebase
  ([`6b9905c`](https://github.com/bhklab/damply/commit/6b9905c1acf8e09d60b3812f3206b909d38178c1))

- Added `pybytesize` dependency to `pyproject.toml`. - Refactored `DirectoryAudit` to use
  `path.stat()` instead of `os.stat()`. - Enhanced documentation in `DamplyDirs` class for better
  clarity on usage and available directories. - Renamed `DirectoryNotFoundError` to
  `DirectoryNameNotFoundError` for better accuracy. - Updated import statement for `ByteSize` to use
  the new package location. - Refactored `damplyplot` function to improve variable naming and
  clarity. - Removed obsolete `ByteSize` class and related tests. - Improved type hints across
  various modules for better code clarity. - Updated exception handling in `whose.py` for better
  error messages. - Cleaned up unused imports and improved code formatting.

### Refactoring

- Comment out Codecov steps in CI workflow for clarity
  ([`368671c`](https://github.com/bhklab/damply/commit/368671c326a809871d7c6636ae5b90691e3753dd))

- Organize imports and improve formatting across multiple files
  ([`6d3d97a`](https://github.com/bhklab/damply/commit/6d3d97af3440659f73bf8672d318ffc1327e5760))

- Rename DirectoryNotFoundError to DirectoryNameNotFoundError for clarity; remove unused test
  ([`b3bd833`](https://github.com/bhklab/damply/commit/b3bd8334ad4ce25f85fab2a7e087e2dc60277013))

- Restore and enable Codecov steps in CI workflow for coverage tracking
  ([`6c7e4ee`](https://github.com/bhklab/damply/commit/6c7e4ee59544b4f1ed06c2a3df09ccfe89cbd44b))


## v0.9.0 (2024-08-20)

### Bug Fixes

- Minor fixes
  ([`ed09859`](https://github.com/bhklab/damply/commit/ed09859ed2db399600c710efaf9b34a7e130548a))

- Minor updates
  ([`1a1d60c`](https://github.com/bhklab/damply/commit/1a1d60cabf9f3987cc4ac16a01e1cd6cc18afbd0))

### Chores

- Update
  ([`9c129ff`](https://github.com/bhklab/damply/commit/9c129ff220177921bfb1f78639f0d35129beebe0))

### Features

- Field adding
  ([`b9780c5`](https://github.com/bhklab/damply/commit/b9780c512425fecd20cbe7b04991ae9b05e93480))


## v0.8.0 (2024-08-01)

### Bug Fixes

- Add tests and fix common root
  ([`3cb4199`](https://github.com/bhklab/damply/commit/3cb4199966275374bbb8b5ab4a93e3a8ba695946))

- Merge
  ([`e6ae533`](https://github.com/bhklab/damply/commit/e6ae53385aad671164427d75edfbe1cb3c1851e4))

- Tests for whose command
  ([`f08d6c2`](https://github.com/bhklab/damply/commit/f08d6c2de2df8a79cd7320aaada18b44c5608c82))

### Chores

- Format and clean
  ([`26bfaf3`](https://github.com/bhklab/damply/commit/26bfaf3b22ed4eaa0c51ab856ff4e1459f1617fb))

### Features

- Add basic audit
  ([`e8c307e`](https://github.com/bhklab/damply/commit/e8c307e3f5e6f5133d1efeabd18f8243f30d82e5))

- Added size check
  ([`219b653`](https://github.com/bhklab/damply/commit/219b6534ba92f42e3e734924e4c2c571c16837ae))

- Init and config subcommands
  ([`578dfda`](https://github.com/bhklab/damply/commit/578dfdaa7ba73d5d865ab2c3a6eea2e2f059cf04))

- Organize cli commands
  ([`e25a966`](https://github.com/bhklab/damply/commit/e25a9664810b385404bb4f2e4ad293db9e1b15b9))


## v0.7.1 (2024-07-31)

### Bug Fixes

- Update cli tool
  ([`9ea8c5a`](https://github.com/bhklab/damply/commit/9ea8c5a9dde55366f2014027dc753f79d9955744))


## v0.7.0 (2024-07-31)

### Bug Fixes

- Fix arrangement
  ([`3e94e4a`](https://github.com/bhklab/damply/commit/3e94e4aff321a5b4fec8e388084565609294b56a))

- Gha to not use locked
  ([`1233f00`](https://github.com/bhklab/damply/commit/1233f00e3ad0e0404ab6513643d3be77c694800c))

- Lint and format and cleanup
  ([`c877847`](https://github.com/bhklab/damply/commit/c877847d18b2f9623b1c963b6f84c7fba4cfba59))

- Update gha to not use locked pixi
  ([`189294e`](https://github.com/bhklab/damply/commit/189294e4883e8fbd65f794461d1ed92e95a12476))

- Update gha to not use locked pixi, add plot to cli
  ([`255e08e`](https://github.com/bhklab/damply/commit/255e08ef8dfaa583ed8946dc41b724759409754d))

### Features

- Add damply plotting
  ([`dcc72e1`](https://github.com/bhklab/damply/commit/dcc72e1bbcd69fe2b4cdc0e9abac8a443f06ca1e))


## v0.6.0 (2024-05-31)

### Bug Fixes

- Lint
  ([`b0abdf4`](https://github.com/bhklab/damply/commit/b0abdf46b416c20f0fb148dd59fadc70761a8815))

- Lock
  ([`4168366`](https://github.com/bhklab/damply/commit/41683662fe792097f017e70013c73d38ded5bf34))

### Features

- Major refactoring of cli
  ([`5998541`](https://github.com/bhklab/damply/commit/5998541bf75be1e7d2fcf8536d1d230dae4919bb))


## v0.5.0 (2024-05-31)

### Chores

- Add tests
  ([`79044ef`](https://github.com/bhklab/damply/commit/79044effb782111c2b1cbccfc21b4a77431d9f5c))

### Features

- Add lazy loading for images in README view
  ([`7d1e053`](https://github.com/bhklab/damply/commit/7d1e053b18f63fbc8c27e6abf813b67eb7f3955d))

- Add whose and file size
  ([`04772d4`](https://github.com/bhklab/damply/commit/04772d49bb4a4ae7656dbb3bb1931a3c76ec544a))


## v0.4.1 (2024-05-31)

### Bug Fixes

- Format
  ([`e153b30`](https://github.com/bhklab/damply/commit/e153b30f32108b0a9750f1a4b0c7e0b00116c152))

- Update metadata table title in cli.py
  ([`a63c36b`](https://github.com/bhklab/damply/commit/a63c36bba26d880abf433cf06690faecb1537d3d))

- Version
  ([`ecefaaf`](https://github.com/bhklab/damply/commit/ecefaafab444f70ace8a8185240d6577fe4db0a3))

### Chores

- Update navigation links in mkdocs.yaml
  ([`931524b`](https://github.com/bhklab/damply/commit/931524b39f8ca9edb971c8a43b84dc858b4a2de8))


## v0.4.0 (2024-05-31)

### Bug Fixes

- Lint
  ([`64944d3`](https://github.com/bhklab/damply/commit/64944d3025cc20721aa5415c882b42e737daa3da))

- Refactor get_file_owner_full_name function for improved error handling and platform compatibility
  ([`f4fca58`](https://github.com/bhklab/damply/commit/f4fca58d63e4667f8c3fc60b51776a038757c669))

### Features

- Add cli whose
  ([`b15ec32`](https://github.com/bhklab/damply/commit/b15ec32b551533aab892b3b3227e2091c643dfe1))

- Update CLI help messages and add 'whose' command
  ([`620f209`](https://github.com/bhklab/damply/commit/620f209656ab91d5f8ae4e11608eaa6aef05e3f9))


## v0.3.0 (2024-05-31)

### Chores

- Delete config/.pypackage-builder-answers.yml
  ([`a04cabd`](https://github.com/bhklab/damply/commit/a04cabd468901e3b47e236a31d9eb867feea7719))

### Features

- Add cli
  ([`1e825d1`](https://github.com/bhklab/damply/commit/1e825d1e71293cb46fcb8abe6498b5a695982e39))

- Add cli tool
  ([`077e52b`](https://github.com/bhklab/damply/commit/077e52bf1e3c529685a631aee6978e59676b0165))


## v0.2.0 (2024-05-31)

### Bug Fixes

- Tests so it makes file
  ([`69d4e54`](https://github.com/bhklab/damply/commit/69d4e54ea76ef75dde242e28261ee79b60bc2093))

### Features

- Add tests and major class
  ([`569177b`](https://github.com/bhklab/damply/commit/569177b476047cadb22ae84d0eeb92ad1fb370ea))

- Refactor metadata.py for improved readability and maintainability
  ([`cf909e0`](https://github.com/bhklab/damply/commit/cf909e0f1824fdc9275171d10c3c2a87049521e7))


## v0.1.1 (2024-05-31)

### Bug Fixes

- Some pypi issues
  ([`c6f810e`](https://github.com/bhklab/damply/commit/c6f810ea4859a45b4d9f1b3432cca1f45dc29f30))


## v0.1.0 (2024-05-31)

### Bug Fixes

- Update gitignore
  ([`97e8fde`](https://github.com/bhklab/damply/commit/97e8fde80ab3a6f38f62a231ffe5fc189983fe05))

### Features

- Add docs and test
  ([`76e92ff`](https://github.com/bhklab/damply/commit/76e92ff24b5e8febb361df0f01d1d063d26ef703))

- Add github actions
  ([`85891c4`](https://github.com/bhklab/damply/commit/85891c4fcd221f3c61874a2c6cec9edc059e94af))

- First commit
  ([`8ed31c9`](https://github.com/bhklab/damply/commit/8ed31c972b3ac76f4def1b02bb50c6fee84a2172))
