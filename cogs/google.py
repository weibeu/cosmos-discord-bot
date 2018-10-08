import discord
import json
from discord.ext import commands
from cogs.utils.checks import embed_perms
from cogs.utils.config import get_config_value
import aiohttp
from cogs.utils import checks
from urllib.parse import quote as uriquote
from urllib.parse import quote_plus
from lxml import etree

'''Module for google web and image search.'''


# Used Rapptz's implementation of google cards.
class Google:

    def __init__(self, bot):
        self.bot = bot

    def parse_google_card(self, node):
        e = discord.Embed(colour=discord.Colour.blurple())

        # check if it's a calculator card:
        calculator = node.find(".//span[@class='cwclet']")
        if calculator is not None:
            e.title = 'Calculator'
            result = node.find(".//span[@class='cwcot']")
            if result is not None:
                result = ' '.join((calculator.text, result.text.strip()))
            else:
                result = calculator.text + ' ???'
            e.description = result
            return e

        # check for unit conversion card

        unit_conversions = node.xpath(".//input[contains(@class, '_eif') and @value]")
        if len(unit_conversions) == 2:
            e.title = 'Unit Conversion'

            # the <input> contains our values, first value = second value essentially.
            # these <input> also have siblings with <select> and <option selected=1>
            # that denote what units we're using

            # We will get 2 <option selected="1"> nodes by traversing the parent
            # The first unit being converted (e.g. Miles)
            # The second unit being converted (e.g. Feet)

            xpath = etree.XPath("parent::div/select/option[@selected='1']/text()")
            try:
                first_node = unit_conversions[0]
                first_unit = xpath(first_node)[0]
                first_value = float(first_node.get('value'))
                second_node = unit_conversions[1]
                second_unit = xpath(second_node)[0]
                second_value = float(second_node.get('value'))
                e.description = ' '.join((str(first_value), first_unit, '=', str(second_value), second_unit))
            except Exception:
                return None
            else:
                return e

        # check for currency conversion card
        if 'currency' in node.get('class', ''):
            currency_selectors = node.xpath(".//div[@class='ccw_unit_selector_cnt']")
            if len(currency_selectors) == 2:
                e.title = 'Currency Conversion'
                # Inside this <div> is a <select> with <option selected="1"> nodes
                # just like the unit conversion card.

                first_node = currency_selectors[0]
                first_currency = first_node.find("./select/option[@selected='1']")

                second_node = currency_selectors[1]
                second_currency = second_node.find("./select/option[@selected='1']")

                # The parent of the nodes have a <input class='vk_gy vk_sh ccw_data' value=...>
                xpath = etree.XPath("parent::td/parent::tr/td/input[@class='vk_gy vk_sh ccw_data']")
                try:
                    first_value = float(xpath(first_node)[0].get('value'))
                    second_value = float(xpath(second_node)[0].get('value'))

                    values = (
                        str(first_value),
                        first_currency.text,
                        f'({first_currency.get("value")})',
                        '=',
                        str(second_value),
                        second_currency.text,
                        f'({second_currency.get("value")})'
                    )
                    e.description = ' '.join(values)
                except Exception:
                    return None
                else:
                    return e

        # check for generic information card
        info = node.find(".//div[@class='_f2g']")
        if info is not None:
            try:
                e.title = ''.join(info.itertext()).strip()
                actual_information = info.xpath("parent::div/parent::div//div[@class='_XWk' or contains(@class, 'kpd-ans')]")[0]
                e.description = ''.join(actual_information.itertext()).strip()
            except Exception:
                return None
            else:
                return e

        # check for translation card
        translation = node.find(".//div[@id='tw-ob']")
        if translation is not None:
            src_text = translation.find(".//pre[@id='tw-source-text']/span")
            src_lang = translation.find(".//select[@id='tw-sl']/option[@selected='1']")

            dest_text = translation.find(".//pre[@id='tw-target-text']/span")
            dest_lang = translation.find(".//select[@id='tw-tl']/option[@selected='1']")

            # TODO: bilingual dictionary nonsense?

            e.title = 'Translation'
            try:
                e.add_field(name=src_lang.text, value=src_text.text, inline=True)
                e.add_field(name=dest_lang.text, value=dest_text.text, inline=True)
            except Exception:
                return None
            else:
                return e

        # check for "time in" card
        time = node.find("./div[@class='vk_bk vk_ans']")
        if time is not None:
            date = node.find("./div[@class='vk_gy vk_sh']")
            try:
                e.title = node.find('span').text
                e.description = f'{time.text}\n{"".join(date.itertext()).strip()}'
            except Exception:
                return None
            else:
                return e

        # time in has an alternative form without spans
        time = node.find("./div/div[@class='vk_bk vk_ans _nEd']")
        if time is not None:
            converted = "".join(time.itertext()).strip()
            try:
                # remove the in-between text
                parent = time.getparent()
                parent.remove(time)
                original = "".join(parent.itertext()).strip()
                e.title = 'Time Conversion'
                e.description = f'{original}...\n{converted}'
            except Exception:
                return None
            else:
                return e

        # check for definition card
        words = node.xpath(".//span[@data-dobid='hdw']")
        if words:
            lex = etree.XPath(".//div[@class='lr_dct_sf_h']/i/span")

            # this one is derived if we were based on the position from lex
            xpath = etree.XPath("../../../ol[@class='lr_dct_sf_sens']//" \
                                "div[not(@class and @class='lr_dct_sf_subsen')]/" \
                                "div[@class='_Jig']/div[@data-dobid='dfn']/span")
            for word in words:
                # we must go two parents up to get the root node
                root = word.getparent().getparent()

                pronunciation = root.find(".//span[@class='lr_dct_ph']/span")
                if pronunciation is None:
                    continue

                lexical_category = lex(root)
                definitions = xpath(root)

                for category in lexical_category:
                    definitions = xpath(category)
                    try:
                        descrip = [f'*{category.text}*']
                        for index, value in enumerate(definitions, 1):
                            descrip.append(f'{index}. {value.text}')

                        e.add_field(name=f'{word.text} /{pronunciation.text}/', value='\n'.join(descrip))
                    except:
                        continue

            return e

        # check for weather card
        location = node.find("./div[@id='wob_loc']")
        if location is None:
            return None


        # these units should be metric

        date = node.find("./div[@id='wob_dts']")

        # <img alt="category here" src="cool image">
        category = node.find(".//img[@id='wob_tci']")

        xpath = etree.XPath(".//div[@id='wob_d']//div[contains(@class, 'vk_bk')]//span[@class='wob_t']")
        temperatures = xpath(node)

        misc_info_node = node.find(".//div[@class='vk_gy vk_sh wob-dtl']")

        if misc_info_node is None:
            return None

        precipitation = misc_info_node.find("./div/span[@id='wob_pp']")
        humidity = misc_info_node.find("./div/span[@id='wob_hm']")
        wind = misc_info_node.find("./div/span/span[@id='wob_tws']")


        try:
            e.title = 'Weather for ' + location.text.strip()
            e.description = f'*{category.get("alt")}*'
            e.set_thumbnail(url='https:' + category.get('src'))

            if len(temperatures) == 4:
                first_unit = temperatures[0].text + temperatures[2].text
                second_unit = temperatures[1].text + temperatures[3].text
                units = f'{first_unit} | {second_unit}'
            else:
                units = 'Unknown'

            e.add_field(name='Temperature', value=units, inline=False)

            if precipitation is not None:
                e.add_field(name='Precipitation', value=precipitation.text)

            if humidity is not None:
                e.add_field(name='Humidity', value=humidity.text)

            if wind is not None:
                e.add_field(name='Wind', value=wind.text)
        except:
            return None

        return e

    async def get_google_entries(self, query):
        url = f'https://www.google.com/search?q={uriquote(query)}'
        params = {
            'safe': 'on',
            'lr': 'lang_en',
            'hl': 'en'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) Gecko/20100101 Firefox/53.0'
        }

        # list of URLs and title tuples
        entries = []

        # the result of a google card, an embed
        card = None

        async with self.bot.session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError('Google has failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())

            # for bad in root.xpath('//style'):
            #     bad.getparent().remove(bad)

            # for bad in root.xpath('//script'):
            #     bad.getparent().remove(bad)

            # with open('google.html', 'w', encoding='utf-8') as f:
            #     f.write(etree.tostring(root, pretty_print=True).decode('utf-8'))

            """
            Tree looks like this.. sort of..
            <div class="rc">
                <h3 class="r">
                    <a href="url here">title here</a>
                </h3>
            </div>
            """

            card_node = root.xpath(".//div[@id='rso']/div[@class='_NId']//" \
                                   "div[contains(@class, 'vk_c') or @class='g mnr-c g-blk' or @class='kp-blk']")

            if card_node is None or len(card_node) == 0:
                card = None
            else:
                card = self.parse_google_card(card_node[0])

            search_results = root.findall(".//div[@class='rc']")
            # print(len(search_results))
            for node in search_results:
                link = node.find("./h3[@class='r']/a")
                if link is not None:
                    # print(etree.tostring(link, pretty_print=True).decode())
                    entries.append((link.get('href'), link.text))

        return card, entries

    @commands.command(aliases=['google'])
    async def g(self, ctx, *, query):
        """Searches google and gives you top result."""
        await ctx.trigger_typing()
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await ctx.send(str(e))
        else:
            if card:
                value = '\n'.join(f'[{title}]({url.replace(")", "%29")})' for url, title in entries[:3])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await ctx.send(embed=card)

            if len(entries) == 0:
                return await ctx.send('No results found... sorry.')

            next_two = [x[0] for x in entries[1:3]]
            first_entry = entries[0][0]
            if first_entry[-1] == ')':
                first_entry = first_entry[:-1] + '%29'

            if next_two:
                formatted = '\n'.join(f'<{x}>' for x in next_two)
                msg = f'{first_entry}\n\n**See also:**\n{formatted}'
            else:
                msg = first_entry

            await ctx.send(msg)

    '''@commands.command(pass_context=True, aliases=['image', 'img'])
    async def i(self, ctx, *, query):
        """Google image search. [p]i Lillie pokemon sun and moon"""
        await ctx.message.delete()
        config = self.bot.config
        if query[0].isdigit():
            item = int(query[0])
            query = query[1:]
        else:
            item = 0
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.googleapis.com/customsearch/v1?q=" + quote_plus(query) + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine'] + "&searchType=image") as resp:
                if resp.status != 200:
                    if not config['google_api_key'] or not config['custom_search_engine']:
                        return await ctx.send("You don't seem to have image searching configured properly. Refer to the wiki for details.")
                    return await ctx.send('Google failed to respond.')
                else:
                    result = json.loads(await resp.text())
                    try:
                        result['items']
                    except:
                        return await ctx.send('There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine.')
                    if len(result['items']) < 1:
                        return await ctx.send('There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine.')
                    em = discord.Embed()
                    if embed_perms(ctx.message):
                        em.set_image(url=result['items'][item]['link'])
                        show_search = get_config_value("config", "show_search_term")
                        if show_search == "True":
                            em.set_footer(text="Search term: \"" + query + "\"")
                        await ctx.send(content=None, embed=em)
                    else:
                        await ctx.send(result['items'][item]['link'])
                        await ctx.send("Search term: \"" + query + "\"")'''

def setup(bot):
    bot.add_cog(Google(bot))
