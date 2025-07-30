# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.3]
### Fixed
- Unread added on every "empty" change bug.

## [0.3.2]
### Fixed
- Flags change logic.

## [0.3.1]
### Fixed
- Attempts to collect stats for `None` recipients.
### Added
- Management command to clear notifications and stats.

## [0.3.0]
### Changed
- Internal stats collect implementation.
### Added
- Management command to recollect stats.
- Notification stats filtering.

## [0.2.0]
### Changed
- Past form of verb "send" changed everywhere from "sended" to "sent".
### Removed
- Removed explicit `pagination_class` from notifications list view.
### Fixed
- Small fixes.

## [0.1.3]
### Fixed
- Django 2.2 compatibility.

## [0.1.1]
Initial version.
