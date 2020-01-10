# Next release

## merge to production 

* commit all changes to develop

* edit makefile.conf
  set PROJECTNAME 

make show-project 

make show-status 

make show-tags 

make archive-release 

make tag-release 

cd GIT/<REPO>

git checkout master 

git merge develop 

git push 

git push --tags 

## next release 

git checkout develop

edit release.txt 







