from typing import List, Optional, Dict, Iterable
import aspose.pycore
import aspose.pydrawing
import aspose.slides
import aspose.slides.ai
import aspose.slides.animation
import aspose.slides.charts
import aspose.slides.dom.ole
import aspose.slides.effects
import aspose.slides.export
import aspose.slides.export.web
import aspose.slides.export.xaml
import aspose.slides.importing
import aspose.slides.ink
import aspose.slides.lowcode
import aspose.slides.mathtext
import aspose.slides.slideshow
import aspose.slides.smartart
import aspose.slides.spreadsheet
import aspose.slides.theme
import aspose.slides.util
import aspose.slides.vba
import aspose.slides.warnings

class IAIWebClient:
    ...

class OpenAIWebClient:
    '''Build-in lightweight OpenAI web client'''
    def __init__(self, model: str, api_key: str, organization_id: str):
        '''Creates instance of OpenAI Web client.
        :param model: OpenAI language model. Possible values:
                      - gpt-4o
                      - gpt-4o-mini
                      - o1
                      - o1-mini
                      - o3
                      - o3-mini
        :param api_key: OpenAI API key
        :param organization_id: Organization ID (optional)'''
        ...

    ...

class SlidesAIAgent:
    '''Provides AI-powered features for processing presentations.'''
    def __init__(self, ai_client: IAIWebClient):
        '''SlidesAIAgent constructor'''
        ...

    def translate(self, presentation: IPresentation, language: str) -> None:
        '''Translates a presentation to the specified language using AI (synchronous version).
        :param presentation: Target presentation
        :param language: Target language'''
        ...

    ...

class SlidesAIAgentException:
    def __init__(self, message: str):
        ...

    ...

