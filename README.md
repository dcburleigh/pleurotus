# pleurotus
Manage a collection of repos related to a projects

## Description

My projects usually are built from more than one git repo.

This tool provides a handy interface to them.

Releases are tagged, with tags of the form <prefix><version>
where <prefix> is an abbrevation of the project name,
and <version> is the release version.

## Use case

project MyProject is built from 2 repos: myproject, mylib.

Another project, ProjectX, is build from 2 repos:  projectx, mylib.


### Commit a release


### Commit secondary repo

## fix

### situation 1
* Beta (development) version is 5.0
* Previous (production) version is 4.9
* repo is missing tag X4.9

* Find date
git flog master..
* assign previous tag
git tag  X4.9  <date>
