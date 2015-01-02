######################## BEGIN LICENSE BLOCK ########################
# The Original Code is Mozilla Communicator client code.
#
# The Initial Developer of the Original Code is
# Netscape Communications Corporation.
# Portions created by the Initial Developer are Copyright (C) 1998
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Mark Pilgrim - port to Python
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301  USA
######################### END LICENSE BLOCK #########################

from .euctwfreq import (EUCTWCharToFreqOrder, EUCTW_TABLE_SIZE,
                        EUCTW_TYPICAL_DISTRIBUTION_RATIO)
from .euckrfreq import (EUCKRCharToFreqOrder, EUCKR_TABLE_SIZE,
                        EUCKR_TYPICAL_DISTRIBUTION_RATIO)
from .gb2312freq import (GB2312CharToFreqOrder, GB2312_TABLE_SIZE,
                         GB2312_TYPICAL_DISTRIBUTION_RATIO)
from .big5freq import (Big5CharToFreqOrder, BIG5_TABLE_SIZE,
                       BIG5_TYPICAL_DISTRIBUTION_RATIO)
from .jisfreq import (JISCharToFreqOrder, JIS_TABLE_SIZE,
                      JIS_TYPICAL_DISTRIBUTION_RATIO)
from .compat import wrap_ord

ENOUGH_DATA_THRESHOLD = 1024
SURE_YES = 0.99
SURE_NO = 0.01
MINIMUM_DATA_THRESHOLD = 3


class CharDistributionAnalysis(object):

    def __init__(self):
        # Mapping table to get frequency order from char order (get from
        # GetOrder())
        self._CharToFreqOrder = None
        self._TableSize = None  # Size of above table
        # This is a constant value which varies from language to language,
        # used in calculating confidence.  See
        # http://www.mozilla.org/projects/intl/UniversalCharsetDetection.html
        # for further detail.
        self._TypicalDistributionRatio = None
        self._Done = None
        self._TotalChars = None
        self._FreqChars = None
        self.reset()

    def reset(self):
        """reset analyser, clear any state"""
        # If this flag is set to True, detection is done and conclusion has
        # been made
        self._Done = False
        self._TotalChars = 0  # Total characters encountered
        # The number of characters whose frequency order is less than 512
        self._FreqChars = 0

    def feed(self, aBuf, aCharLen):
        """feed a character with known length"""
        if aCharLen == 2:
            # we only care about 2-bytes character in our distribution analysis
            order = self.get_order(aBuf)
        else:
            order = -1
        if order >= 0:
            self._TotalChars += 1
            # order is valid
            if order < self._TableSize:
                if 512 > self._CharToFreqOrder[order]:
                    self._FreqChars += 1

    def get_confidence(self):
        """return confidence based on existing data"""
        # if we didn't receive any character in our consideration range,
        # return negative answer
        if self._TotalChars <= 0 or self._FreqChars <= MINIMUM_DATA_THRESHOLD:
            return SURE_NO

        if self._TotalChars != self._FreqChars:
            r = (self._FreqChars / ((self._TotalChars - self._FreqChars)
                 * self._TypicalDistributionRatio))
            if r < SURE_YES:
                return r

        # normalize confidence (we don't want to be 100% sure)
        return SURE_YES

    def got_enough_data(self):
        # It is not necessary to receive all data to draw conclusion.
        # For charset detection, certain amount of data is enough
        return self._TotalChars > ENOUGH_DATA_THRESHOLD

    def get_order(self, aBuf):
        # We do not handle characters based on the original encoding string,
        # but convert this encoding string to a number, here called order.
        # This allows multiple encodings of a language to share one frequency
        # table.
        return -1


class EUCTWDistributionAnalysis(CharDistributionAnalysis):
    def __init__(self):
        super(EUCTWDistributionAnalysis, self).__init__()
        self._CharToFreqOrder = EUCTWCharToFreqOrder
        self._TableSize = EUCTW_TABLE_SIZE
        self._TypicalDistributionRatio = EUCTW_TYPICAL_DISTRIBUTION_RATIO

    def get_order(self, aBuf):
        # for euc-TW encoding, we are interested
        #   first  byte range: 0xc4 -- 0xfe
        #   second byte range: 0xa1 -- 0xfe
        # no validation needed here. State machine has done that
        first_char = wrap_ord(aBuf[0])
        if first_char >= 0xC4:
            return 94 * (first_char - 0xC4) + wrap_ord(aBuf[1]) - 0xA1
        else:
            return -1


class EUCKRDistributionAnalysis(CharDistributionAnalysis):
    def __init__(self):
        super(EUCKRDistributionAnalysis, self).__init__()
        self._CharToFreqOrder = EUCKRCharToFreqOrder
        self._TableSize = EUCKR_TABLE_SIZE
        self._TypicalDistributionRatio = EUCKR_TYPICAL_DISTRIBUTION_RATIO

    def get_order(self, aBuf):
        # for euc-KR encoding, we are interested
        #   first  byte range: 0xb0 -- 0xfe
        #   second byte range: 0xa1 -- 0xfe
        # no validation needed here. State machine has done that
        first_char = wrap_ord(aBuf[0])
        if first_char >= 0xB0:
            return 94 * (first_char - 0xB0) + wrap_ord(aBuf[1]) - 0xA1
        else:
            return -1


class GB2312DistributionAnalysis(CharDistributionAnalysis):
    def __init__(self):
        super(GB2312DistributionAnalysis, self).__init__()
        self._CharToFreqOrder = GB2312CharToFreqOrder
        self._TableSize = GB2312_TABLE_SIZE
        self._TypicalDistributionRatio = GB2312_TYPICAL_DISTRIBUTION_RATIO

    def get_order(self, aBuf):
        # for GB2312 encoding, we are interested
        #  first  byte range: 0xb0 -- 0xfe
        #  second byte range: 0xa1 -- 0xfe
        # no validation needed here. State machine has done that
        first_char, second_char = wrap_ord(aBuf[0]), wrap_ord(aBuf[1])
        if (first_char >= 0xB0) and (second_char >= 0xA1):
            return 94 * (first_char - 0xB0) + second_char - 0xA1
        else:
            return -1


class Big5DistributionAnalysis(CharDistributionAnalysis):
    def __init__(self):
        super(Big5DistributionAnalysis, self).__init__()
        self._CharToFreqOrder = Big5CharToFreqOrder
        self._TableSize = BIG5_TABLE_SIZE
        self._TypicalDistributionRatio = BIG5_TYPICAL_DISTRIBUTION_RATIO

    def get_order(self, aBuf):
        # for big5 encoding, we are interested
        #   first  byte range: 0xa4 -- 0xfe
        #   second byte range: 0x40 -- 0x7e , 0xa1 -- 0xfe
        # no validation needed here. State machine has done that
        first_char, second_char = wrap_ord(aBuf[0]), wrap_ord(aBuf[1])
        if first_char >= 0xA4:
            if second_char >= 0xA1:
                return 157 * (first_char - 0xA4) + second_char - 0xA1 + 63
            else:
                return 157 * (first_char - 0xA4) + second_char - 0x40
        else:
            return -1


class SJISDistributionAnalysis(CharDistributionAnalysis):
    def __init__(self):
        super(SJISDistributionAnalysis, self).__init__()
        self._CharToFreqOrder = JISCharToFreqOrder
        self._TableSize = JIS_TABLE_SIZE
        self._TypicalDistributionRatio = JIS_TYPICAL_DISTRIBUTION_RATIO

    def get_order(self, aBuf):
        # for sjis encoding, we are interested
        #   first  byte range: 0x81 -- 0x9f , 0xe0 -- 0xfe
        #   second byte range: 0x40 -- 0x7e,  0x81 -- oxfe
        # no validation needed here. State machine has done that
        first_char, second_char = wrap_ord(aBuf[0]), wrap_ord(aBuf[1])
        if (first_char >= 0x81) and (first_char <= 0x9F):
            order = 188 * (first_char - 0x81)
        elif (first_char >= 0xE0) and (first_char <= 0xEF):
            order = 188 * (first_char - 0xE0 + 31)
        else:
            return -1
        order = order + second_char - 0x40
        if second_char > 0x7F:
            order = -1
        return order


class EUCJPDistributionAnalysis(CharDistributionAnalysis):
    def __init__(self):
        super(EUCJPDistributionAnalysis, self).__init__()
        self._CharToFreqOrder = JISCharToFreqOrder
        self._TableSize = JIS_TABLE_SIZE
        self._TypicalDistributionRatio = JIS_TYPICAL_DISTRIBUTION_RATIO

    def get_order(self, aBuf):
        # for euc-JP encoding, we are interested
        #   first  byte range: 0xa0 -- 0xfe
        #   second byte range: 0xa1 -- 0xfe
        # no validation needed here. State machine has done that
        char = wrap_ord(aBuf[0])
        if char >= 0xA0:
            return 94 * (char - 0xA1) + wrap_ord(aBuf[1]) - 0xa1
        else:
            return -1
