Our standard aims to meet the FAIR and CARE principles, and adds a few of our own, the DeAR principles. Paralex was inspired by the [
Cross-Linguistic Data Formats
(CLDF)](https://cldf.clld.org/) standard, and adheres to a similar philosophy.

The [FAIR principles](https://www.go-fair.org/fair-principles/) are meant to ensure that datasets are both readable by machines
and by humans across sub-fields, disciplines and time. Here is a very short summary of the FAIR principles and how this standard aims to meet them:

- **A**ccessible: Data must have a persistent global identifier (F1), be described by rich metadata (F2) which include the identifier (F3), and be indexed in searchable resources (F4).
  - F1/F4: We suggest using [zenodo](https://zenodo.org/) to get a DOI and archive your data.
  - F2/F3: The standard uses [json](https://en.wikipedia.org/wiki/JSON) metadata, following the [frictionless](http://frictionlessdata.io/) standard.
**I**nteroperable: Use a formal, accessible, shared, broadly applicable language for knowledge representation (I1), use FAIR vocabularies (I2) and refer to other (meta)data (I3).
    - I1: We write the metadata in [json](https://en.wikipedia.org/wiki/JSON), the tables in [csv](https://frictionlessdata.io/blog/2018/07/09/csv/), and respect the [frictionless](http://frictionlessdata.io/) standard
  - I2: The standard documents our conventions and columns, providing a FAIR vocabulary.
  - I2/I3: The standard comes with built-in linking to other resources and encourages references to other resources and linking to other vocabularies such as [gold ontology](http://linguistics-ontology.org/gold),  [unimorph schema](https://unimorph.github.io/schema/), [universal dependency tagset](https://universaldependencies.org/u/overview/morphology.html), [CLTS' BIPA](https://clts.clld.org/contributions/bipa), [glottocodes](https://glottolog.org/), [ISO codes for languages](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes), etc.
- **R**eusable: Data should be well described (R1) so that they can be re-used and combined in other contexts. This standard's main aim is to ensure that the data is richly and consistently described.

Because the FAIR principles make sure the data is widely shared and reused, and usable computationally, they focus on **data users**. However, two more group of people are relevant when producing language datasets: Indigenous communities and dataset authors.

The [CARE Principles for Indigenous Data Governance](https://www.gida-global.org/care) focus on the interests of the language communities whose languages are described by our datasets. They are meant to be compatible with FAIR principles. These are not principles that can be fullfilled simply by adhering to a formal standard, but rather require careful planning and engagement with language communities. In short, they state:

## DeAR

Beyond users and speakers, language data also needs to be planned in ways that are good for the dataset authors. Thus, we introduced the **DeAR** principles:

### **De**centralized

Data is decentralised with no single team or institution operating a central database. 
The standard serves as a format to **share** data and as a means for researchers to 
create interoperable data of high-quality. We wish to make the standard 
as easy to use as possible, and to useful tools to its users.


###  **A**utomated verification

Data is [tested automatically](tutorial.md#Validating)
against the descriptions in the metadata in order to guarantee data quality. Moreover,
data quality can be checked by writing
custom [tests](tutorial.md#Testing) (as is done in software development), which are run
after each change of the data. 

### **R**evisable pipelines

Dataset authors must be able to continuously update
data presentation, in particular websites, reflecting the evolving nature of data. This is achieved by generating those
publications automatically and directly from the standardized dataset. We will create automated tools
which can generate user-friendly views of the data (for example static
websites, publication ready pdfs, etc.). These can be run again at any point, so that 
it is easy to re-generate those from the data edited by the researchers.

Both principes **A** and **R** fit particularly well with the use of versioning
systems such as [git](https://git-scm.com/), where validation, testing and publishing can be done through
continuous development pipelines.
