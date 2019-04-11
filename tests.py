import unittest

from keywords_tokenizer import tokenize_one, STOPWORDS

class TestKeywordsTokenizerArchitectureData(unittest.TestCase):
    def setUp(self):
        self.text = """Strategically located in the Cultural Centre of the Nation (CCN) – next to the National Museum, the Ministry of Education, the new headquarters of the National Bank or the Huaca San Borja – the design of the LCC was to satisfy four strategic objectives: being a cultural and economic motor for the country, representing a meeting place at the heart of the city enrooted in the collective Peruvian culture, turning into a unique, flexible and technologically advanced architectonic landmark and finally, triggering the urban transformation of the CNN and its surroundings. The near 15,000 m2 of net area correspond to the 18 multipurpose convention halls, their sizes and proportions varying from 3,500 m2 to 100 m2, which allow for up to 10,000 people to attend simultaneous events. """

    def test_tokenize(self):
        expected = """strategically located!cultural centre!nation!ccn!next!national museum!ministry!education!new headquarters!national bank!huaca san borja!design!lcc!satisfy!strategic objectives!cultural!economic motor!country!representing!meeting place!heart!city enrooted!collective peruvian culture!turning!unique!flexible!technologically advanced architectonic landmark!finally!triggering!urban transformation!cnn!surroundings!near!m2!net area correspond!multipurpose convention halls!sizes!proportions varying from!m2!m2!allow!people!attend simultaneous events"""
        self.assertEqual(tokenize_one(self.text), expected)

    def test_tokenize_other_stopwords(self):
        expected = """strategically located!cultural centre!nation!ccn!next!national museum!ministry!education!new headquarters!national bank!huaca san borja!design!lcc!satisfy four strategic objectives!cultural!economic motor!country!representing!meeting place!heart!city enrooted!collective peruvian culture!turning!unique!flexible!technologically advanced architectonic landmark!finally!triggering!urban transformation!cnn!surroundings!near!net area correspond!multipurpose convention halls!sizes!proportions varying!allow!people!attend simultaneous events"""

        self.assertEqual(tokenize_one(self.text, STOPWORDS["en"] + ["m2", "from"]), expected)

class TestKeywordsTokenizerHealthData(unittest.TestCase):
    def setUp(self):
        self.text = """Because ejection fraction (EF) is one of the most important predictors of survival in patients with left ventricular (LV) dysfunction and because Packer showed a large reduction in mortality figures with carvedilol, in contrast to former studies with bisoprolol and metoprolol, we investigated if this difference in survival may be related to a difference in improvement of LV function by different beta-blockers. We searched the MEDLINE database and all reference lists of articles obtained through the search for the relation between beta-blocker treatment and improvement in EF. Forty-one studies met the criteria and we added two of our own studies. Four hundred and fifty-eight patients were treated with metoprolol with a mean follow-up of 9.5 months and a mean increase in EF of 7.4 EF units. One thousand thirty patients were treated with carvedilol with a mean follow up of 7 months and a mean increase in EF of 5.7 EF units. One hundred ninety-nine patients were treated with bucindolol with a mean follow-up of 4 months and a mean increase in EF of 4.6 EF units. Several small studies with nebivolol, atenolol, and propranolol were also studied and, when combined, the mean increase in EF was 8.6 EF units. When patients with idiopathic and ischemic cardiomyopathies were compared, the average increase in EF units was 8.5 vs. 6.0, respectively. The use of beta-blocker treatment in heart failure patients, irrespective of the etiology, improved LV function in almost all studies and it appears that the differences among beta-blockers and among etiologies is small and probably insignificant. However, there is a difference in survival rate when the various beta-blockers are compared, suggesting that mechanisms other than improvement of LV function by beta-blockers are responsible for the difference in survival."""
        self.text2 = """clinical trial design--effect of prone positioning on clinical outcomes in infants and children with acute respiratory distress syndrome
purpose: this paper describes the methodology of a clinical trial of prone positioning in pediatric patients with acute lung injury (ali)
nonrandomized studies suggest that prone positioning improves oxygenation in patients with ali/acute respiratory distress syndrome without the risk of serious iatrogenic injury
it is not known if these improvements in oxygenation result in improvements in clinical outcomes
"""

    def test_tokenize(self):
        expected = """ejection fraction!ef!important predictors!survival!patients!left ventricular!lv!dysfunction!packer!large reduction!mortality figures!carvedilol!contrast!former studies!bisoprolol!metoprolol!investigated!difference!survival!related!difference!improvement!lv function!different beta-blockers!searched!medline database!reference lists!articles!search!relation!beta-blocker treatment!improvement!ef!studies met!criteria!added!studies!hundred!patients!treated!metoprolol!mean follow!months!mean increase!ef!ef units!thousand!patients!treated!carvedilol!mean follow!months!mean increase!ef!ef units!hundred!patients!treated!bucindolol!mean follow!months!mean increase!ef!ef units!small studies!nebivolol!atenolol!propranolol!studied!combined!mean increase!ef!ef units!patients!idiopathic!ischemic cardiomyopathies!compared!average increase!ef units!vs!respectively!beta-blocker treatment!heart failure patients!irrespective!etiology!improved lv function!studies!appears!differences!beta-blockers!etiologies!small!probably insignificant!difference!survival rate!beta-blockers!compared!suggesting!mechanisms!improvement!lv function!beta-blockers!responsible!difference!survival"""
        self.assertEqual(tokenize_one(self.text), expected)

    def test_tokenize2(self):
        expected = """clinical trial design--effect!prone positioning!clinical outcomes!infants!children!acute respiratory distress syndrome
purpose!paper describes!methodology!clinical trial!prone positioning!pediatric patients!acute lung injury!ali
nonrandomized studies suggest!prone positioning improves oxygenation!patients!ali!acute respiratory distress syndrome!risk!serious iatrogenic injury
known!improvements!oxygenation result!improvements!clinical outcomes
"""
        self.assertEqual(tokenize_one(self.text2), expected)
