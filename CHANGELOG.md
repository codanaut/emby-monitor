# Changelog
All notable changes to this project will be documented in this file, if i remember. 


## Testing Branch

## 2020-9-2
### Added
- settings.example
- CHANGELOG.md

### Changed
- added settings.ini to ignore and changed to example so its not over written when updated
- changed readme to reflect changes
- changed size of movie poster box


## 2020-9-3
### Changed
- changed tv poster to thumbnail when only one stream is playing
- cleaned up old sections of code

### Fixed
- fixed issue with users that have no activity yet causing keyerror to stop loading rest of sections
- added exception for weird, random glitch where device doesnt report back last active time/date
