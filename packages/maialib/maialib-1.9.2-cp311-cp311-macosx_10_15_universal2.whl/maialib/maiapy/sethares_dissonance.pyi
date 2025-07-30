import pandas as pd
import plotly
import plotly.graph_objects as go
from maialib import maiacore as mc
from typing import Callable

def plotSetharesDissonanceCurve(fundamentalFreq: float = 440, numPartials: int = 6, ratioLowLimit: float = 1.0, ratioHighLimit: float = 2.3, ratioStepIncrement: float = 0.001, amplCallback: Callable[[list[float]], list[float]] | None = None) -> tuple[go.Figure, pd.DataFrame]:
    """
    Compute the Sethares Dissonance Curve of a given base frequency

    Return
        A tuple that contains a Plotly figure, and the pair 'ratios' and 'dissonance' lists
    """
def plotScoreSetharesDissonance(score: mc.Score, plotType: str = 'line', lineShape: str = 'linear', numPartialsPerNote: int = 6, useMinModel: bool = True, amplCallback: Callable[[list[float]], list[float]] | None = None, dissCallback: Callable[[list[float]], float] | None = None, **kwargs) -> tuple[go.Figure, pd.DataFrame]:
    '''Plot 2D line graph of the Sethares Dissonance over time

    Args:
       score (maialib.Score): A maialib Score object loaded with a valid MusicXML file
       plotType (str): Can be \'line\' or \'scatter\'
       lineShape (str): Can be \'linear\' or \'spline\'
       numPartialsPerNote (int): Amount of spectral partials for each note
       useMinModel (bool): Sethares dissonance values can be computed using the \'minimal amplitude\' model
                    or the \'product amplitudes\' model. The \'min\' model is a more recent approach
       amplCallback: Custom user function callback to generate the amplitude of each spectrum partial
       dissCallback: Custom user function callback to receive all paired partial dissonances and computes 
                     a single total dissonance value output
    Kwargs:
       measureStart (int): Start measure to plot
       measureEnd (int): End measure to plot
       numPoints (int): Number of interpolated points

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> myScore = ml.Score("/path/to/score.xml")
    >>> ml.plotScoreSetharesDissonance(myScore)
    >>> ml.plotScoreSetharesDissonance(myScore, numPoints=15)
    >>> ml.plotScoreSetharesDissonance(myScore, measureStart=10, measureEnd=20)
    '''
def plotChordDyadsSetharesDissonanceHeatmap(chord: mc.Chord, numPartialsPerNote: int = 6, useMinModel: bool = True, amplCallback: Callable[[list[float]], list[float]] | None = None, dissonanceThreshold: float = 0.1, dissonanceDecimalPoint: int = 2) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]:
    '''Plot chord dyads Sethares dissonance heatmap

    Args:
       chord (maialib.Chord):  A maialib Chord

    Kwargs:
       numPartialsPerNote (int): Amount of spectral partials for each note
       useMinModel (bool): Sethares dissonance values can be computed using the \'minimal amplitude\' model
                    or the \'product amplitudes\' model. The \'min\' model is a more recent approach
       amplCallback: Custom user function callback to generate the amplitude of each spectrum partial
       dissonanceThreshold (float): Dissonance threshold to skip small dissonance values
       dissonanceDecimalPoint (int): Round chord dissonance value in the plot title

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> import maialib as ml
    >>> myChord = ml.Chord(["C3", "E3", "G3"])
    >>> fig, df = plotChordDyadsSetharesDissonanceHeatmap(myChord)
    >>> fig.show()
    '''
