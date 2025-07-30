from yta_web_scraper import ChromeScraper
from yta_programming.path import DevPathHandler
from yta_programming.output import Output
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_constants.file import FileExtension, FileParsingMethod, FileType
from yta_general.dataclasses import FileReturned
from selenium.webdriver.common.by import By
from random import randrange
from typing import Union
from time import strftime, gmtime


class YoutubeImageGenerator:
    """
    Class to generate images from Youtube platform.
    """

    @staticmethod
    def generate_comment(
        author: str = None,
        avatar_url: str = None,
        time: str = None,
        message: str = None,
        likes_number: int = None,
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        """
        This method generates a Youtube comment image with the provided
        information. It will return the image read with PIL, but will
        also store the screenshot (as this is necessary while processing)
        with the provided 'output_filename' if provided, or with as a
        temporary file if not.
        """
        author = (
            # TODO: Fake author name (starts with @)
            'Juanillo'
            if not author else
            author
        )

        avatar_url = (
            # TODO: Fake avatar_url or just let the one existing
            'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmIVOqsYK3t8HxkQ_WjwPoP2cwJiV1xDyWIw&s'
            if not avatar_url else
            avatar_url
        )

        time = (
            # TODO: Fake time ('hace X años,meses,dias,horas')
            'hace 3 horas'
            if not time else
            time
        )

        message = (
            # TODO: Fake a message with AI
            'Esto es un mensaje de ejemplo, fakeado, pasa el tuyo propio por favor.'
            if not message else
            message
        )

        likes_number = (
            randrange(50)
            if not likes_number else
            likes_number
        )

        scraper = ChromeScraper(False)
        # We go to this specific video with comments available
        scraper.go_to_web_and_wait_until_loaded('https://www.youtube.com/watch?v=OvUj2WsADjI')
        # We need to scroll down to let the comments load
        # TODO: This can be better, think about a more specific strategy
        # about scrolling
        scraper.scroll_down(1000)
        scraper.wait(1)
        scraper.scroll_down(1000)
        scraper.wait(1)

        # We need to make sure the comments are load
        scraper.find_element_by_element_type_waiting('ytd-comment-thread-renderer')
        comments = scraper.find_elements_by_element_type('ytd-comment-thread-renderer')

        comment = comments[2]
        body = comment.find_element(By.ID, 'body')

        # Change user (avatar) image
        image = body.find_element(By.ID, 'img')
        scraper.set_element_attribute(image, 'src', avatar_url)
        # TODO: Check that Image actually changes in the view
        # maybe with this: https://stackoverflow.com/questions/44286061/how-to-check-that-the-image-was-changed-if-therere-no-changes-in-html-code

        # Change date
        time_element = body.find_element(By.ID, 'published-time-text')
        time_element = scraper.find_element_by_element_type('a', time_element)
        scraper.set_element_inner_text(time_element, time)

        # Change user name
        author_element = body.find_element(By.ID, 'header-author')
        author_element = scraper.find_element_by_element_type('h3', author_element)
        author_element = scraper.find_element_by_element_type('a', author_element)
        author_element = scraper.find_element_by_element_type('span', author_element)
        scraper.set_element_inner_text(author_element, author)

        # Change message
        message_element = scraper.find_element_by_id('content-text', comment)
        message_element = scraper.find_element_by_element_type('span', message_element)
        scraper.set_element_inner_text(message_element, message)

        # Change number of likes
        likes_element = scraper.find_element_by_id('vote-count-middle', comment)
        scraper.set_element_inner_text(likes_element, str(likes_number))
        
        scraper.scroll_to_element(comment)
        
        output_filename = Output.get_filename(output_filename, FileExtension.PNG)
        
        style = 'width: 500px; padding: 10px;'
        scraper.set_element_style(comment, style)
        scraper.screenshot_element(comment, output_filename)

        return FileReturned(
            # TODO: This was previously...
            # content = Image.open(output_filename),
            content = None,
            filename = output_filename,
            output_filename = output_filename,
            type = FileType.IMAGE,
            is_parsed = False,
            # TODO: None or 'PILLOW_IMAGE'? It is an image
            # but it can be opencv also...
            parsing_method = None,
            extra_args = None
        )

    @requires_dependency('yta_google_drive_downloader', 'yta_image_advanced', 'yta_google_drive_downloader')
    @staticmethod
    def generate_thumbnail(
        title: str = None,
        image_url: str = None,
        channel_name: str = None,
        channel_image_url: str = None,
        duration_in_seconds: int = None,
        views: str = None,
        time_since_publication: str = None,
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        from yta_google_drive_downloader.resource import Resource

        title = (
            # TODO: Fake it
            'Título de la miniatura'
            if not title else
            title
        )

        image_url = (
            # TODO: Fake it
            'https://static-cse.canva.com/blob/1697393/1600w-wK95f3XNRaM.jpg'
            if not image_url else
            image_url
        )

        channel_name = (
            # TODO: Fake it
            'Youtube Autónomo'
            if not channel_name else
            channel_name
        )

        channel_image_url = (
            # TODO: Fake it
            'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmIVOqsYK3t8HxkQ_WjwPoP2cwJiV1xDyWIw&s'
            if not channel_image_url else
            channel_image_url
        )

        duration_in_seconds = (
            randrange(300, 700)
            if not duration_in_seconds else
            duration_in_seconds
        )

        views = (
            # TODO: Fake it
            '2.3M visitas'
            if not views else
            views
        )

        time_since_publication = (
            # TODO: Fake it
            'hace 2 horas'
            if not time_since_publication else
            time_since_publication
        )

        scraper = ChromeScraper()
        # Go to https://thumbnailchecker.com/es
        scraper.go_to_web_and_wait_until_loaded('https://thumbnailchecker.com/es')

        # Fill info (we need it to be able to see the modal)
        title_input = scraper.find_element_by_class('input', 'form_input')
        title_input.send_keys('Título de prueba')
        upload_input = scraper.find_element_by_id('upload')
        # This is just an Image to set it, but then we change
        # it for the real one
        # TODO: Is this ok (?)
        filename = Resource.get('https://drive.google.com/file/d/1rcowE61X8c832ynh0xOt60TH1rJfcJ6z/view?usp=drive_link', 'base_thumbnail.png')
        scraper.set_file_input(upload_input, f'{DevPathHandler.get_project_abspath()}{filename}')

        button = scraper.find_element_by_text_waiting('button', 'Revisa tu miniatura')
        scraper.scroll_to_element(button)
        button.click()

        thumbnail_container_element = scraper.find_element_by_class_waiting('div', 'yt_main_box')

        # Image
        image = scraper.find_element_by_class('div', 'yt_box_thumbnail', thumbnail_container_element)
        image = scraper.find_element_by_element_type('div', image)
        image = scraper.find_element_by_element_type('img', image)
        scraper.set_element_attribute(image, 'src', image_url)
        # TODO: Wait loading (?)

        # Avatar image
        avatar_image = scraper.find_element_by_class('div', 'yt_box_info_avatar', thumbnail_container_element)
        avatar_image = scraper.find_element_by_element_type('img', avatar_image)
        scraper.set_element_attribute(avatar_image, 'src', channel_image_url)
        # TODO: Wait loading (?)

        # Video duration (in 'MM:SS' format)
        video_duration_element = scraper.find_element_by_class('span', 'yt_time_status')
        duration_str = strftime('%M:%S', gmtime(duration_in_seconds))
        if duration_in_seconds >= 3600:
            duration_str = strftime('%H:%M:%S', gmtime(duration_in_seconds))
            if duration_in_seconds < 36000:
                # We need to set hour as one only digit
                duration_str = duration_str[1:]
        scraper.set_element_inner_text(video_duration_element, duration_str)

        # Title
        description = scraper.find_element_by_class('div', 'yt_box_info_content', thumbnail_container_element)
        title_element = scraper.find_element_by_element_type('h4', description)
        scraper.set_element_inner_text(title_element, title)

        # Author
        user = scraper.find_element_by_element_type('p', description)
        scraper.set_element_inner_text(user, channel_name)

        # Views
        views_element = scraper.find_element_by_class('div', 'yt_box_info_meta', thumbnail_container_element)
        ul = scraper.find_element_by_element_type('ul', views_element)
        listed_items = scraper.find_elements_by_element_type('li', ul)
        # TODO: Handle 'views' and 'time_since_publication' with int
        # and format it manually here
        scraper.set_element_inner_text(listed_items[1], views)
        scraper.set_element_inner_text(listed_items[2], time_since_publication)

        style = 'width: 500px; padding: 10px;'
        scraper.set_element_style(thumbnail_container_element, style)

        output_filename = Output.get_filename(output_filename, FileExtension.PNG)

        scraper.screenshot_element(thumbnail_container_element, output_filename)

        return FileReturned(
            # TODO: This was previously...
            # content = Image.open(output_filename),
            content = None,
            filename = output_filename,
            output_filename = output_filename,
            type = FileType.IMAGE,
            is_parsed = False,
            # TODO: None or 'PILLOW_IMAGE'? It is an image
            # but it can be opencv also...
            parsing_method = None,
            extra_args = None
        )