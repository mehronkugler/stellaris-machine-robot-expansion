This is a continuation of XVCV's "Machines & Robot Expansion" mod for Stellaris. The goals are to keep it up to date with the latest game version, fix bugs, and add new content.

The original author has abandoned the work and is no longer available for contact.

# Welcome

I (openly-retro) am a web developer by day, and a fan of Stellaris. I enjoy science fiction a lot.

I invite you to collaborate, but I also want you to know I'm not desperate for help and this mod will continue to thrive even if you only just stop by to say hi.

## Communicating

Chat with me about this mod in the [Stellaris Modding Den](https://discord.gg/vKwNs93g ) discord! Look for `mag-sanchusa#4206 (openlyretro)`. We can discuss this mod in the `machines-robots-expac` channel.

I will also respond to comments in the Github wiki and issues for this project.

## Contributing

Please visit the Github repo wiki for this project: [https://github.com/openly-retro/stellaris-machine-robot-expansion/wiki](https://github.com/openly-retro/stellaris-machine-robot-expansion/wiki)

Warnings about working with Clausewitz syntax (what base Stellaris traits files are written in)

- It MAKES UP ITS OWN RULES
- IT MAY NOT FOLLOW THE RULES IT MAKES
- It wiLL DaNcE On yOuR SaNiTy
- You may lose yourself to possession of a psionic avatar if you stare too long or try to apply your ideas of "rules" and "well this could be standardized pretty easily"

## Translations

Welcome translators!! I am very happy to have you here.

If you would like to submit a translation, please go ahead and create a pull request from a fork of this repo.

The translation files should go in:

`localisation/<language>/replace`

So if you are translating Korean files, the changes should go in `localisation/korean/replace/` because I have a language copy tool which copies all changes from English to all other languge folders.

If you place the files in `localisation/<language>` and not in `localisation/<language>/replace` then the files will be overwritten.

If they are in the `replace` folder then your correctly translated files will always take precedence over the English version. If your translation files are missing any keys then the missing keys will show up in English.

This way, players will never see only the localisation key with no content if there are translations missing.

### Patches

I do updates using the concept of patches. A patch consists of:

1. A group of bug fixes or small features, OR
2. A large feature

Workflow:

1. Create a branch for the patch, following the next in the series at https://github.com/openly-retro/stellaris-machine-robot-expansion/tags (if 2.3.2 is the latest then the next is 2.3.3), named `patch-#.#.#` where #.#.# is the patch version
2. Do some work in your feature or bug branch and then make a pull request to the patch branch

# Art Credits

- https://pixabay.com/illustrations/water-technology-sci-fi-futuristic-7547817/ by [https://pixabay.com/users/joker39-30858803/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7547817](Melvyn Thevenin) from [https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7547817"](Pixabay) , used for World Machine planetary deposits and other artworks
- https://pixabay.com/illustrations/futuristic-architecture-wallpaper-6694976/ by  <a href="https://pixabay.com/users/tommyvideo-3092371/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=6694976">Tomislav Jakupec</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=6694976">Pixabay</a>, used for World Machine technology art
- https://pixabay.com/illustrations/blueprint-engineering-technology-6944719/ by Image by <a href="https://pixabay.com/users/xresch-7410129/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=6944719">Reto Scheiwiller</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=6944719">Pixabay</a>, used for World Machine event art
- https://pixabay.com/illustrations/futuristic-background-pattern-7831598/ Image by <a href="https://pixabay.com/users/placidplace-25572496/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7831598">Peace,love,happiness</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7831598">Pixabay</a>, used for World Machine art
- https://pixabay.com/illustrations/fantastic-technology-futuristic-4805591/ Image by <a href="https://pixabay.com/users/gtuignatov-3540393/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=4805591">Alexander Ignatov</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=4805591">Pixabay</a>
- https://pixabay.com/illustrations/blur-background-pattern-geometric-7281360/ Image by <a href="https://pixabay.com/users/placidplace-25572496/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7281360">Peace,love,happiness</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7281360">Pixabay</a>, used for World Machine event art
- [https://www.deviantart.com/xxaries1970xx/art/Digital-Circuit-936780185](Digital Circuit, by XxAries1970xX) , used for the Source Code Reprogramming event-related banners and other artworks.

# Code generation workflow (The Good Stuff)

Things like button effects, custom GUI code, and trait tooltips need to be automated. It is too punishing to require 1 human brain to update everything by hand. To this end, I created a number of Python scripts that generate some of the code for this mod.

What does the Python code pipeline do?

1. Collect base game trait files and reformat the PDX Script into something sane and predictable
2. Trim down trait data, sort it, dump it to JSON for organizing
3. Sort and order all the traits into three output files, deciding which traits are for each of the 3 custom GUI types
4. Look at the base game to find the correct capitalizations for modifiers
5. Find Machine-specific tooltips and trait names
6. A whole lot of miscellaneous stuff for solving headaches, corner cases, and dealing with inconsistencies
7. Generate button effects for all custom GUIs and place into `common/scripted_effects/`
8. Generate tooltips for all custom GUIs and place into `localisation/english/` folder
9. Stitch together custom GUI files and place them in `interface/` folder

Run: 

`python .\run_mre_trait_pipeline.py --stellaris_path <YOUR_STEAM_FOLDER>\steamapps\common\Stellaris\`

See [BUILD.md](BUILD.md) for details of what to do after the pipeline run has finished.
