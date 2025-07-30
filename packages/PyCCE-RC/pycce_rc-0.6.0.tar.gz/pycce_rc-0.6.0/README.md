# PyCCE-RC

PyCCE-RC is a Python package implementing the Common Correlated Effects (CCE)[2] estimators for panel data models with unobserved common factors. The package also incorporates a recently proposed rank condition (RC) test[1], alongside their proposed augmentation algorithm[1] designed to restore the RC when violated. PyCCE-RC supports all three CCE estimators and enables verification of the RC assumption critical for estimator consistency.

[1]: De Vos, I., Everaert, G., Sarafidis, V.  (2024). *[A method to evaluate the rank condition for CCE estimators](https://www.tandfonline.com/doi/full/10.1080/07474938.2023.2292383)*.

[2]: Pesaran, M. H. (2006). *[Estimation and Inference in Large Heterogeneous Panels with a Multifactor Error Structure](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1468-0262.2006.00692.x?casa_token=a4DN2RZkTSYAAAAA%3AKu-6rvAIXhXz267YLnmEst5RCt8frPLfQSqJpIWccR4UOWI_Qg_NlQNdyiDuqv_PtJYs9wvLlKGWe0_g)*.

## 📦 Features

- Implementation of all three CCE estimators:
  - **Individual-specific CCE**
  - **Mean Group CCE**
  - **Pooled CCE**

- Built-in tools for:
  - Verifying the **rank condition** (RC test)
  - Performing **augmentation algorithm** to (potentially) restore the RC

- Compatible with balanced and unbalanced panel data

- Modular design:
  - `py_cce.base`: core data structures and base for estimation logic
  - `py_cce.models`:  estimator classes
  - `py_cce.utils`: CSA computation, rank condition testing, and other utilities

⚠️ Note: Some numerical instabilities may occur during estimation, affecting both the estimator classes and the rank condition test. These issues are known and will be addressed in future versions.

## 🛠 Installation

```bash
pip install pycce-rc
```

## 👤 Author

**Merijn Huiskes**

Email: [merijnhuiskes1@gmail.com](mailto:merijnhuiskes1@gmail.com)

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).
See the [LICENSE](./LICENSE) file for details.
