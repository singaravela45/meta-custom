# meta-custom

## Overview

`meta-custom` is a custom Yocto/OpenEmbedded layer developed to provide application-level integration and additional configurations for Yocto-based embedded Linux systems.

The primary purpose of this layer is to maintain custom application recipes, systemd service integration, and related configurations required to deploy and run applications on embedded devices.

## Supported Yocto Releases

This repository maintains separate branches for different Yocto Project releases.

Please switch to the appropriate branch based on the Yocto release you are using:

| Yocto Release | Branch |
|---|---|
| Wrynose | `wrynose` |
| Scarthgap | `scarthgap` |

**Important:** Make sure to switch to the correct release branch before using or modifying the layer.

For example:

```bash
git switch wrynose
```

or

```bash
git switch scarthgap
```

## Layer Contents

The layer contains custom recipes and configurations for integrating applications into Yocto-based embedded Linux images.

Depending on the release branch, the layer may include:

- Application installation recipes.
- Python application integration.
- Required application files and models.
- systemd service integration for automatic application startup.
- Release-specific configurations and modifications.

## Contributions and Improvements

Contributions are welcome!

If you have improvements, bug fixes, or application integration requirements, feel free to contribute.

In particular, contributions are welcome for:

- Adding support for additional Yocto releases.
- Modifying existing recipes to improve compatibility.
- Adding support for new applications.
- Improving systemd service integration.
- Fixing bugs and improving existing configurations.
- Updating documentation and installation instructions.

When adding support for a different Yocto release, please maintain a separate branch and ensure that the recipes are compatible with the corresponding release.

## Contributing

1. Clone the repository.
2. Switch to the appropriate Yocto release branch.
3. Make the required modifications.
4. Test the recipes with the corresponding Yocto release.
5. Submit your changes through a pull request.

All contributions and suggestions are welcome.

## License

Refer to the individual recipes and their respective license declarations for licensing information.
