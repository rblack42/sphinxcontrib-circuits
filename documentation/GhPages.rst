Publishing Project Documentation on GitHub
##########################################

:Reference: http://raxcloud.blogspot.com/2013/02/documenting-python-code-using-sphinx.html

GitHub_ offers a free website for project pages to all open source projects.
This is an ideal place to post documentation for your project, and it is easy
to set up when using Sphinx.

In this note, I will show how to set up the documentaiton for a project I am
working on: `sphinxcontrib-circuits`_. Much of this material is derived from a
post I found (referenced above).

Once the project is on GitHub_ do this:

..  code-block:: text

    $ mkdir gh_pages
    $ /usr/local/share/git-core/contrib/workdir/git-new-workdir . gh-pages/html
    $ cd gh_pages/html
    $ git checkout --orphan gh_pages
    $ git rm -rf .

Now, switch back to the top od the project and do this:

..  code-block:: text

    make html
    cd gh-pages/html
    touch .nojekyll
    git add .
    git commit -am 'Initial commit of docs'
    git push -u origin gh-pages 
   
Once you push your docs to GitHUb_ navigate to a link like
http://rblack42.github.io/sphinxcontrib-circuits/ to see the pages. This can
take a while to get published by GitHub_. 

..  sphinxcontrib-circuits: https://sphinxcontrib-circuits.github.io/
