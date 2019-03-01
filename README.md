# pleurotus
Manage a collection of repos related to a project. 

Provide an opionated control of releases.

## Description

My projects usually are built from more than one git repo.

This tool provides a handy interface to them.

Releases are tagged, with tags of the form <prefix><version>
where <prefix> is an abbrevation of the project name,
and <version> is the release version.

## Use case

project MyProject is built from 2 repos: myproject, mylib.

Another project, ProjectX, is build from 2 repos:  projectx, mylib.

## Configure

Edit the YAML-formatted project configuration file, projects.yml.

(see the example in scripts/projects.example.yml)

## usage

see:
    pydoc gp

### Status

Check status of a project

make show-project PROJECTNAME=...



### Commit a release

* commit all changes in primary repo
* commit ? changes in related repos
* check

make show-details

make verify

* archive commit logs 
    
make archive-release 

* tag

make tag-release
        
* merge to production

cd GIT/project

git checkout master

git merge develop

git push
git push --tags

* begin next release
git checkout develop
edit release.txt
   increment version

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

### change tag prefix
https://stackoverflow.com/questions/1028649/how-do-you-rename-a-git-tag#5719854

old tag prefix is x
repo has 2 existing release tags,
   x1.0
   x1.1

new prefix is y
* @dev
  git tag y1.0 x1.0
  git tag -d  x1.0
  git push origin :refs/tags/x1.0


* @all
  git pull --prune --tags
