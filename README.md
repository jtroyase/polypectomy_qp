PQP Annotation Tool
====================

Software that allows you to manually and quickly annotate images.
It is designed to specifically generate data to train an AI to recognize the quality of the polypectomy and identify polyps.
The program is based on PyQt5.

-----------

### Building dependencies
* [Qt](https://www.qt.io/) = 5.15.7
* [pyqtgraph](https://www.pyqtgraph.org/) = 0.12.3
* [Pandas](https://pandas.pydata.org/) = 1.5.2
* [Numpy](https://numpy.org/) =1.23.5

Tested on Ubuntu 18.04.6 LTS
Processor: Intel® Core™ i7-9700K CPU @ 3.60GHz × 8
Graphics: Quadro P620/PCIe/SSE2

### Installation

#### Linux

1. Clone the repository
2. Open terminal in the folder of the project.
3. ```pip install -r requirements.txt```


### License :

GNU Lesser General Public License v3.0 

Permissions of this copyleft license are conditioned on making available complete source code of licensed works and modifications under the same license or the GNU GPLv3. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights. However, a larger work using the licensed work through interfaces provided by the licensed work may be distributed under different terms and without source code for the larger work.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


### Citation :

```bib
  {
    author = {Troya J.},
    institution = {University Hospital of Würzburg}
    title = {Image Annotation Tool for predicting the quality of polypectomies},
    howpublished = "\url{https://github.com/jtroyase/polypectomy_qp}",
    year = {2023},
  }
```