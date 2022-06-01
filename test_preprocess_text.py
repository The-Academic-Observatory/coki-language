import unittest

from predict_language import preprocess_text


class TestTextPreProcessing(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(preprocess_text(""), "")
        self.assertEqual(preprocess_text("  "), "")
        self.assertEqual(preprocess_text("\n"), "")
        self.assertEqual(preprocess_text("\t"), "")

    def test_no_title_available(self):
        # Should be removed by SQL query anyway
        self.assertEqual(preprocess_text("[NO TITLE AVAILABLE]"), "")
        self.assertEqual(preprocess_text(" [NO TITLE AVAILABLE] "), "")

    def test_url(self):
        self.assertEqual(preprocess_text("https://open.coki.ac"), "")
        self.assertEqual(preprocess_text("http://open.coki.ac"), "")
        self.assertEqual(preprocess_text(" http://open.coki.ac "), "")

    def test_doi(self):
        self.assertEqual(preprocess_text("10.13003/5jchdy"), "")
        self.assertEqual(preprocess_text(" 10.13003/5jchdy "), "")
        self.assertNotEqual(
            preprocess_text("Exploring the Mysteries of 10.13003/5jchdy Cannabis through Gas Chromatography"), ""
        )
        self.assertNotEqual(
            preprocess_text("10.13003/5jchdy Exploring the Mysteries of Cannabis through Gas Chromatography"), ""
        )
        self.assertNotEqual(
            preprocess_text(
                "Exploring the Mysteries of 10.13003/5jchdy Cannabis through Gas Chromatography 10.13003/5jchdy"
            ),
            "",
        )

    def test_html_escape(self):
        title = "Cytologic diagnosis of vaginal stump fallopian tube prolapse after hysterectomy&amp;mdash;A case report&amp;mdash;"
        expected = "Cytologic diagnosis of vaginal stump fallopian tube prolapse after hysterectomy—A case report—"
        actual = preprocess_text(title)
        self.assertEqual(expected, actual)

    def test_html_strip(self):
        title = "Exploring the Mysteries of <i>Cannabis</i> through Gas Chromatography"
        expected = "Exploring the Mysteries of Cannabis through Gas Chromatography"
        actual = preprocess_text(title)
        self.assertEqual(expected, actual)

    def test_remove_internal_whitespace(self):
        title = "Convolution on L\n                      p-spaces of a locally compact group"
        expected = "Convolution on L p-spaces of a locally compact group"
        actual = preprocess_text(title)
        self.assertEqual(expected, actual)

    def test_remove_xml(self):
        title = 'Mapping the deposition of <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" altimg="si1.svg"><mml:mrow><mml:mmultiscripts><mml:mtext>C</mml:mtext><mml:mprescripts /><mml:none /><mml:mn>137</mml:mn></mml:mmultiscripts><mml:mtext>s</mml:mtext></mml:mrow></mml:math> and <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" altimg="si2.svg"><mml:mrow><mml:mmultiscripts><mml:mtext>I</mml:mtext><mml:mprescripts /><mml:none /><mml:mn>131</mml:mn></mml:mmultiscripts></mml:mrow></mml:math> in North America following the 2011 Fukushima Daiichi Reactor accident'
        expected = "Mapping the deposition of C137s and I131 in North America following the 2011 Fukushima Daiichi Reactor accident"
        actual = preprocess_text(title)
        self.assertEqual(expected, actual)

    def test_remove_crossref_abstract_markup(self):
        abstract = "<jats:title>Abstract</jats:title>\n<jats:p>Background: Oprozomib (OPZ) is a selective oral proteasome inhibitor that binds selectively and irreversibly to its target. In a phase 1b/2 study of single-agent OPZ in patients (pts) with hematologic malignancies, OPZ has shown promising"
        expected = "Abstract Background: Oprozomib (OPZ) is a selective oral proteasome inhibitor that binds selectively and irreversibly to its target. In a phase 1b/2 study of single-agent OPZ in patients (pts) with hematologic malignancies, OPZ has shown promising"
        actual = preprocess_text(abstract)
        self.assertEqual(expected, actual)

    # def test_remove_latex(self):
    #     title = "Measurement of the $e^+e^- \to \omega\eta$ cross section below $\sqrt{s}=2$ GeV"
    #     expected = "Measurement of the e^+e^- o ωη cross section below √(s)=2 GeV"
    #     actual = preprocess_text(title)
    #     self.assertEqual(expected, actual)

    def test_remove_non_utf8(self):
        title = "Fruit yield of European cranberry (Oxycoccus palustris Pers.) in different plant communities of peatlands (Northern Wielkopolska, Poland). The aim of this study was to determine fruit yield of Oxycoccus palustris under the climatic and habitat conditions of northern Wielkopolska (the Greater Poland region), depending on the type of occupied plant community. Total fruit number and fruit weight as well as average cranberry leaf size were determined on 33 plots with an area of 1 m2, located on 7 peatlands. On the study areas, European cranberry produced crops from 9.2 up to 242.0 g \udbc0\udc89\udbc0\udc03 m-2, which gives 92-2420 kg \udbc0\udc89\udbc0\udc03ha-1. It has been demonstrated that on the peatlands of northern Wielkopolska O. palustris reaches its generative and vegetative optimum in the communities of the class Scheuchzerio- Caricetea fuscae, in particular in the community Sphagno recurvi-Eriophoretum angustifolii.\n"
        expected = "Fruit yield of European cranberry (Oxycoccus palustris Pers.) in different plant communities of peatlands (Northern Wielkopolska, Poland). The aim of this study was to determine fruit yield of Oxycoccus palustris under the climatic and habitat conditions of northern Wielkopolska (the Greater Poland region), depending on the type of occupied plant community. Total fruit number and fruit weight as well as average cranberry leaf size were determined on 33 plots with an area of 1 m2, located on 7 peatlands. On the study areas, European cranberry produced crops from 9.2 up to 242.0 g  m-2, which gives 92-2420 kg ha-1. It has been demonstrated that on the peatlands of northern Wielkopolska O. palustris reaches its generative and vegetative optimum in the communities of the class Scheuchzerio- Caricetea fuscae, in particular in the community Sphagno recurvi-Eriophoretum angustifolii."
        actual = preprocess_text(title)
        self.assertEqual(expected, actual)
