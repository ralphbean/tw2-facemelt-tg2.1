
import tw2facemelttg21.model as model
from tw2.jqplugins.jqgrid import SQLAjqGridWidget

from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import categoryAxisRenderer_js, barRenderer_js
from tw2.core import JSSymbol

class LogGrid(SQLAjqGridWidget):
    id = 'awesome-loggrid'
    entity = model.ServerHit
    excluded_columns = ['id']
    datetime_format = "%x %X"

    prmFilter = {'stringResult': True, 'searchOnEnter': False}

    options = {
        'pager': 'awesome-loggrid_pager',
        'url': '/jqgrid/',
        'rowNum':15,
        'rowList':[15,150, 1500],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 525,
        'height': 'auto',
    }

class LogPlot(JQPlotWidget):
    id = 'awesome-logplot'

    options = {
        'seriesDefaults' : {
            'renderer': JSSymbol('$.jqplot.BarRenderer'),
            'rendererOptions': { 'barPadding': 4, 'barMargin': 10 }
        },
        'axes' : {
            'xaxis': {
                'renderer': JSSymbol(src="$.jqplot.CategoryAxisRenderer"),
            },
            'yaxis': {'min': 0, },
        }
    }

    def prepare(self):
        self.resources.append(categoryAxisRenderer_js)
        self.resources.append(barRenderer_js)
        super(LogPlot, self).prepare()
