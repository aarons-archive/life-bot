#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from typing import Union

import slate
import spotify


class SearchResult:

    __slots__ = 'source', 'search_type', 'search_result', 'tracks'

    def __init__(self, source: str, search_type: str, search_result: Union[spotify.Album, spotify.Playlist, spotify.Track, list[slate.Track], slate.Playlist],
                 tracks: list[slate.Track]) -> None:

        self.source = source
        self.search_type = search_type
        self.search_result = search_result
        self.tracks = tracks

    def __repr__(self) -> str:
        return f'<life.SearchResult source={self.source} search_type={self.search_type} search_result={self.search_result}>'
