import unittest
import os
import time
from Orange.widgets.tests.base import WidgetTest
from orangecontrib.text import Corpus
from Orange.widgets.utils.widgetpreview import WidgetPreview
from PyQt5.QtTest import QTest

from orangecontrib.nlp.widgets.owanaliza_sentymentu import OWAnalizaSentymentu

class TestOWTEIXMLTokenExtractor(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(OWAnalizaSentymentu)

    def test_token_extraction(self):
        input_data = Corpus(os.path.join("datasets", "recenzja_produktu.tab"))
        reference_table = Corpus(os.path.join("datasets", "answer.tab"))

        # Set the input on the widget
        self.send_signal("Korpus", input_data, self.widget)
        self.widget.handleNewSignals()

        # Wait for the worker to complete
        timeout = 30  # seconds
        start_time = time.time()
        while self.widget.worker is not None and self.widget.worker.isRunning():
            if time.time() - start_time > timeout:
                self.fail("Worker did not complete in time")
            QTest.qWait(3000)

        output = self.get_output(self.widget.Outputs.data)
        self.assertIsNotNone(output)

        # Compare output to reference
        self.assertEqual(len(output), len(reference_table), "Row count mismatch")
        self.assertEqual(len(output.domain.attributes), len(reference_table.domain.attributes),
                         "Column count mismatch")

        # Compare values approximately
        for row_out, row_ref in zip(output, reference_table):
            for val_out, val_ref in zip(row_out, row_ref):
                self.assertAlmostEqual(val_out, val_ref, places=3)

if __name__ == "__main__":
    unittest.main()
