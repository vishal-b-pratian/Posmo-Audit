from re import M
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from content_management.models import *
from configuration.models import Channel
import json

from content_management.components.scrapper import Scrapper
# from content_management.components.content_analyser import ContentAnalyser
from content_management.components.practice import ContentAnalyser


@api_view(['GET', 'POST'])
def LinksViewSet(request):
   if request.method == 'POST':
      links = Links.objects.all()
      channel_id = request.data.get('channel_id', None)
      if not channel_id:
         return Response('Channel ID not sent', status=status.HTTP_400_BAD_REQUEST)

      serializer = LinksSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      validated_data = serializer.validated_data
      channel_obj =  Channel.objects.filter(id=channel_id).first()
      validated_data['channel'] = channel_obj

      link_obj = Links.objects.create(**validated_data)
      url = validated_data['url']
      link = Links.objects.get(channel_id=channel_id)
      try:
      # parameters = json.load(link.parameters)
         parameters = eval(serializer.data['parameters'])
         scraper = Scrapper()
         scrape_data = scraper.scrapeURL(url)[0]

         content = Content.objects.create(link=link, main_content=scrape_data)

         contents = ContentAnalyser(scrape_data, parameters)

         processed_words = contents.preprocessing()
         content_info = ContentFetchInfo.objects.create(content=content, processed_words=processed_words)

         mapped_keywords = contents.audit_frequency()
         mapped_keywords_count = contents.count_mapped_keywords()
         MappedKeyWords.objects.create(content_info=content_info,
                                       mapped_keywords=mapped_keywords, mapped_keywords_count=mapped_keywords_count)

         unmapped_keywords = contents.final_unmapped()
         unmapped_keywords_count = len(unmapped_keywords)
         UnmappedKeywords.objects.create(
               content_info=content_info, unmapped_keywords=unmapped_keywords, unmapped_keywords_count=unmapped_keywords_count)

         return Response("Fetch Complete", status=status.HTTP_201_CREATED)
      except:
         link_obj.delete()
         return Response("Internal Logic error", status=status.HTTP_501_NOT_IMPLEMENTED)
   if request.method == 'GET':
         links = Links.objects.all()
         serializer = LinksSerializer(links, many=True)
         return Response(serializer.data)


@api_view(['GET'])
def View_Keyword_Summary(request, channel_id):
    if request.method == 'GET':
        contentfetchmapped = MappedKeyWords.objects.all()
        contentfetchUnmapped = UnmappedKeywords.objects.all()

        if channel_id is not None:
            contentfetchmapped = contentfetchmapped.filter(
                content_info__content__link__channel_id__icontains=channel_id)
            contentfetchUnmapped = contentfetchUnmapped.filter(
                content_info__content__link__channel_id__icontains=channel_id)

        contentfetch_mapped_serializer = ContentFetchMappedSerializer(contentfetchmapped, many=True)
        contentfetch_unmapped_serializer = ContentFetchUnmappedSerializer(contentfetchUnmapped, many=True)

        try:
            map_count = contentfetch_mapped_serializer.data[0]['mapped_keywords_count']
            unmap_count = contentfetch_unmapped_serializer.data[0]['unmapped_keywords_count']
            total_count = map_count + unmap_count

            Count_dict = dict()
            Count_dict['total_words_count'] = eval(total_count)
            Count_dict['mapped_keywords_count'] = eval(map_count)
            Count_dict['unmapped_keywords_count'] = eval(unmap_count)

            return Response(Count_dict)
        except:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def Content_Fetch_Unmapped(request, channel_id):
    if request.method == 'GET':
        contentfetch = UnmappedKeywords.objects.all()
        if channel_id is not None:
            contentfetch = contentfetch.filter(content_info__content__link__channel_id__icontains=channel_id)
        try:
            contentfetch_serializer = ContentFetchUnmappedSerializer(contentfetch, many=True)
            list_unmapped = contentfetch_serializer.data[0]['unmapped_keywords']
            return Response(eval(list_unmapped))
        except:
            return Response("Not Found", status=status.HTTP_404_NOT_FOUND)

# class ContentViewSet(viewsets.ModelViewSet):
#    queryset = Content.objects.all()
#    serializer_class = ContentSerializer

# class ContentViewSet(viewsets.ModelViewSet):
#    queryset = Content.objects.all()
#    serializer_class = ContentSerializer

# class ContentViewSet(viewsets.ModelViewSet):
#    queryset = Content.objects.all()
#    serializer_class = ContentSerializer
