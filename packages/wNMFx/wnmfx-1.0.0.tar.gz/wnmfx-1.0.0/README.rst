wNMFx: Weighted Non-Negative Matrix Factorization
=================================================

About
-----
*wNMFx* implements a simple version of Non-Negative Matrix Factorization (NMF)
that utilizes a weight matrix to weight the importance of each feature
in each sample of the data matrix to be factorized.

*wNMFx* is easy to use, because it behaves like an `sklearn.decomposition` model,
but also allows for multiple fitting attempts.

More information about the modified multiplicative update algorithim utilized can be found here:
`Blondel, Vincent & Ho, Ngoc-Diep & Van Dooren, Paul. (2007). Weighted Nonnegative Matrix Factorization and Face Feature Extraction <https://pdfs.semanticscholar.org/e20e/98642009f13686a540c193fdbce2d509c3b8.pdf>`_

*wNMFx* specifically implements solutions for determining the
decomposed matrices U and V when minimizing the Frobenius Norm
or the Kullback-Leibler Divergence:

wNMF was developed by SN: https://github.com/asn32/weighted-nmf.
wNMFx is a fork which speeds up the computation with jax.
wNMFx follows the scikit-learn conventions.
Additional features include transform().

Useful Links
------------
- `Source on Github <https://github.com/JohannesBuchner/weighted-nmf-jax>`_
- `Package on PyPI <https://pypi.org/project/wNMFx/>`_

.. image:: https://img.shields.io/pypi/v/wNMFx.svg
        :target: https://pypi.python.org/pypi/wNMFx

.. image:: https://github.com/JohannesBuchner/weighted-nmf-jax/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/JohannesBuchner/weighted-nmf-jax/actions/workflows/tests.yml

.. image:: https://img.shields.io/badge/docs-published-ok.svg
        :target: https://github.com/JohannesBuchner/weighted-nmf-jax/
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/JohannesBuchner/weighted-nmf-jax/badge.svg?branch=main
        :target: https://coveralls.io/github/JohannesBuchner/weighted-nmf-jax?branch=main
        :alt: Coverage

Installation
------------
This package is available on PyPI and can be installed with *pip*::

      $ pip install wNMFx

Alternatively, download the source from `github <https://github.com/JohannesBuchner/weighted-nmf-jax>`_ and install::

      $ git clone https://github.com/JohannesBuchner/weighted-nmf-jax
      $ cd weighted-nmf-jax
      $ python3 setup.py install --user

Usage
-----
`wNMFx` is a python library that can be imported::

      from wNMFx import wNMF

And it can be used like an `sklearn.decomposition` model.

First create an instance of the `wNMF` model by setting the number of components.

Other parameters can be set too, such as the loss function,
maximum number of iterations, and whether or not to track
the decreasing error over every single run::

      ## Mock data, a 100x100 data matrix, reduce to 25 dimensions
      n = 100
      features = 100
      components = 25
      X = 100 * np.random.uniform(size=(features, n))
      W = np.ones_like(X)

      ## Define the model / fit
      model = wNMF(n_components=25,
                  beta_loss='kullback-leibler',
                  max_iter=1000,
                  track_error=True)

Then, fit the model to the data using the instance methods `wNMF().fit` or `wNMF().fit_transform`::

      fit = model.fit(X=X,W=W,n_run=5)

After the fit is complete, explore the fit quality by examining
the decomposed matrices and / or overall error::

      ## Get the best solutions
      lowest_error = fit.err
      best_V = fit.V
      best_U = fit.U

      ## Or look at all the solutions from the 5 runs in this example
      all_Vs = fit.V_all

License
-------
wNMFx is MIT-licensed

Disclaimer
----------
`wNMFx` is provided with no guarantees.

