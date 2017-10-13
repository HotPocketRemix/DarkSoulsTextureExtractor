# Dark Souls Texture Extractor
Unpacks Dark Souls 1 texture files from the unpacked game files, bypassing DSFix's texture dump feature to grab all textures all at once. This means the user doesn't have
to visit every area, equip every item, etc. to dump their textures; the game does not need to even be started.

Instructions:

Note: The Dark Souls 1 data directory `DATA` is usually located at `C:\Program Files (x86)\Steam\SteamApps\common\Dark Souls Prepare to Die Edition\DATA`, but it may be in
a different location depending on your Steam installation.

Before beginning, make sure you have at least 10GB of free hard-disk space and 1GB of available RAM to run UDSFM, and 2 additional GB of free hard-disk space for the texture files.

* If you have not done so already, use [UnpackDarkSoulsForModding](https://github.com/HotPocketRemix/UnpackDarkSoulsForModding) to unpack your Dark Souls files. **Important Note**: Many texture files are inside the *bnd files. To make the contents of these files available to the unpacker, you **must** answer "No" when UDSFM asks if you want to delete temporary files.
* If on Windows, download `dist/DarkSoulsTextureExtractor.exe` and `dist/superfasthash.dll` and place them in your `DATA` directory.
* If on Linux, you will need to run from Python source and `dist/superfasthash.so` instead.
* Run `DarkSoulsTextureExtractor.exe` by double-clicking on it. A command prompt windows should appear.
* Do not close the window until the prompt indicates that the process has completed. Make sure you read any prompts carefully before answering.

Once the tool completes, you may delete `DarkSoulsTextureExtractor.exe` and `dist/superfasthash.dll` from `DATA`.

The output files are placed in `DATA\unpacked-textures` and are grouped into three sub-directories, `textures` for plain texture files, `normals` for normal maps, and `speculars` for specular maps.
These classifications are based on the true file name (that is, the name of the texture file as it appears in the unpacked files) and so is not guaranteed to be 100% accurate.

Technical Notes:

The distributed library superfasthash is compiled C implementing the SuperFastHash hashing algorithm that DSFix uses to name its texture files. This is implemented in C to provide a significant speed boost over a pure Python implementation.
