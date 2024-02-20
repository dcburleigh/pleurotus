# Next release

## merge to production

* commit all changes to develop

* edit makefile.conf
  set PROJECTNAME

## preview

make show-project

make show-status
  commit any uncommitted files for P or T repos

make show-tags

## document

make archive-release

review files in GL/<tag>/<version>

* mantis.txt
  update related wiki pages,
  set status to Prod

## merge

make tag-release

* primary repos

cd GIT/<REPO>

git checkout master

git merge develop

git push

git push --tags

* tracking repos

* related
?

## document

update wiki


## next release

* primary

git checkout develop

edit release.txt
