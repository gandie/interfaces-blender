# Interfaces Blender import

[Derived from](https://github.com/simonbroggi/blender_spreadsheet_import)

Import [Interfaces](https://github.com/gandie/interfaces-docker) JSON files to Blender,
use Interfaces choreoraphy data in geometry nodes. 

Have fun tinkering with Interfaces data, example records and project infos
can be found [here](https://interfaces.7pc.de/).

# Installation

## Release zip file

Donwload release zip file from releases page.
Install via Preferences -> Add-ons - "Install from disk",
OR drag & drop zip file into blender window to trigger installation.

## Manual installation

Create new folder in your Blender extensions, e.g.:

```
C:\Users\lars\AppData\Roaming\Blender Foundation\Blender\4.3\extensions\blender_org\interfaces_import
```

Copy content from repository to new folder and retart Blender. Extension shows
up in settings and can be activated / deactivated.

# Usage

After installation you can press F3 and search for "Interfaces import" or use
the file menu: `"File" -> "Import" -> "Interfaces import (.json)"`.

Pick the Interfaces export JSON file of your choice and set mandatory fields
to be imported, which is mostly `x`, `y` and `z` coordinates.

JSON import options can be left empty in most cases, as no array name is
required for Interfaces files (they already ship as array of frames, each
frame is an array of joint coordinates), encoding default should be correct
in 101% of use cases.

Optionally use "Joint Names" to further filter the import file, check
Blazepose model docs for joint names, all upper case and seperated by
underscore, e.g. `LEFT_EAR` or `RIGHT_ELBOW`.

[Blazepose Model](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model)

[Example nodes to extract a specific field](https://github.com/simonbroggi/blender_spreadsheet_import?tab=readme-ov-file#example-node-setup)
