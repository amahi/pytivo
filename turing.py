# Turing Encryption for Python, v1.4
# Copyright 2013 William McBrine
# Based on material Copyright 2002 Qualcomm Inc., written by Greg Rose
#
# License from original C version:
# --------------------------------
#
# This software is free for commercial and non-commercial use subject to
# the following conditions:
#
# 1.  Copyright remains vested in QUALCOMM Incorporated, and Copyright
# notices in the code are not to be removed.  If this package is used in
# a product, QUALCOMM should be given attribution as the author of the
# Turing encryption algorithm. This can be in the form of a textual
# message at program startup or in documentation (online or textual)
# provided with the package.
#
# 2.  Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# a. Redistributions of source code must retain the copyright notice,
#    this list of conditions and the following disclaimer.
#
# b. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
#
# c. All advertising materials mentioning features or use of this
#    software must display the following acknowledgement: This product
#    includes software developed by QUALCOMM Incorporated.
#
# 3.  THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE AND AGAINST
# INFRINGEMENT ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# 4.  The license and distribution terms for any publically available
# version or derivative of this code cannot be changed, that is, this
# code cannot simply be copied and put under another distribution
# license including the GNU Public License.
#
# 5.  The Turing family of encryption algorithms are covered by patents
# in the United States of America and other countries. A free and
# irrevocable license is hereby granted for the use of such patents to
# the extent required to utilize the Turing family of encryption
# algorithms for any purpose, subject to the condition that any
# commercial product utilising any of the Turing family of encryption
# algorithms should show the words "Encryption by QUALCOMM" either on
# the product or in the associated documentation.

""" Turing Encryption for Python

    A Python implementation of Qualcomm's Turing pseudo-random number
    generator. Loosely based on Greg Rose's TuringFast.c et al. This is
    immensely slower than the C version, but useful for some limited
    purposes. For Python 2.5 through 2.7.

"""

__author__ = 'William McBrine <wmcbrine@gmail.com>'
__version__ = '1.4'

import struct
from itertools import izip

# 8->32 _SBOX generated by Millan et. al. at Queensland University of
# Technology. See: E. Dawson, W. Millan, L. Burnett, G. Carter, "On the
# Design of 8*32 S-boxes". Unpublished report, by the Information
# Systems Research Centre, Queensland University of Technology, 1999.

_QBOX = [
    0x1faa1887, 0x4e5e435c, 0x9165c042, 0x250e6ef4, 0x5957ee20, 0xd484fed3,
    0xa666c502, 0x7e54e8ae, 0xd12ee9d9, 0xfc1f38d4, 0x49829b5d, 0x1b5cdf3c,
    0x74864249, 0xda2e3963, 0x28f4429f, 0xc8432c35, 0x4af40325, 0x9fc0dd70,
    0xd8973ded, 0x1a02dc5e, 0xcd175b42, 0xf10012bf, 0x6694d78c, 0xacaab26b,
    0x4ec11b9a, 0x3f168146, 0xc0ea8ec5, 0xb38ac28f, 0x1fed5c0f, 0xaab4101c,
    0xea2db082, 0x470929e1, 0xe71843de, 0x508299fc, 0xe72fbc4b, 0x2e3915dd,
    0x9fa803fa, 0x9546b2de, 0x3c233342, 0x0fcee7c3, 0x24d607ef, 0x8f97ebab,
    0xf37f859b, 0xcd1f2e2f, 0xc25b71da, 0x75e2269a, 0x1e39c3d1, 0xeda56b36,
    0xf8c9def2, 0x46c9fc5f, 0x1827b3a3, 0x70a56ddf, 0x0d25b510, 0x000f85a7,
    0xb2e82e71, 0x68cb8816, 0x8f951e2a, 0x72f5f6af, 0xe4cbc2b3, 0xd34ff55d,
    0x2e6b6214, 0x220b83e3, 0xd39ea6f5, 0x6fe041af, 0x6b2f1f17, 0xad3b99ee,
    0x16a65ec0, 0x757016c6, 0xba7709a4, 0xb0326e01, 0xf4b280d9, 0x4bfb1418,
    0xd6aff227, 0xfd548203, 0xf56b9d96, 0x6717a8c0, 0x00d5bf6e, 0x10ee7888,
    0xedfcfe64, 0x1ba193cd, 0x4b0d0184, 0x89ae4930, 0x1c014f36, 0x82a87088,
    0x5ead6c2a, 0xef22c678, 0x31204de7, 0xc9c2e759, 0xd200248e, 0x303b446b,
    0xb00d9fc2, 0x9914a895, 0x906cc3a1, 0x54fef170, 0x34c19155, 0xe27b8a66,
    0x131b5e69, 0xc3a8623e, 0x27bdfa35, 0x97f068cc, 0xca3a6acd, 0x4b55e936,
    0x86602db9, 0x51df13c1, 0x390bb16d, 0x5a80b83c, 0x22b23763, 0x39d8a911,
    0x2cb6bc13, 0xbf5579d7, 0x6c5c2fa8, 0xa8f4196e, 0xbcdb5476, 0x6864a866,
    0x416e16ad, 0x897fc515, 0x956feb3c, 0xf6c8a306, 0x216799d9, 0x171a9133,
    0x6c2466dd, 0x75eb5dcd, 0xdf118f50, 0xe4afb226, 0x26b9cef3, 0xadb36189,
    0x8a7a19b1, 0xe2c73084, 0xf77ded5c, 0x8b8bc58f, 0x06dde421, 0xb41e47fb,
    0xb1cc715e, 0x68c0ff99, 0x5d122f0f, 0xa4d25184, 0x097a5e6c, 0x0cbf18bc,
    0xc2d7c6e0, 0x8bb7e420, 0xa11f523f, 0x35d9b8a2, 0x03da1a6b, 0x06888c02,
    0x7dd1e354, 0x6bba7d79, 0x32cc7753, 0xe52d9655, 0xa9829da1, 0x301590a7,
    0x9bc1c149, 0x13537f1c, 0xd3779b69, 0x2d71f2b7, 0x183c58fa, 0xacdc4418,
    0x8d8c8c76, 0x2620d9f0, 0x71a80d4d, 0x7a74c473, 0x449410e9, 0xa20e4211,
    0xf9c8082b, 0x0a6b334a, 0xb5f68ed2, 0x8243cc1b, 0x453c0ff3, 0x9be564a0,
    0x4ff55a4f, 0x8740f8e7, 0xcca7f15f, 0xe300fe21, 0x786d37d6, 0xdfd506f1,
    0x8ee00973, 0x17bbde36, 0x7a670fa8, 0x5c31ab9e, 0xd4dab618, 0xcc1f52f5,
    0xe358eb4f, 0x19b9e343, 0x3a8d77dd, 0xcdb93da6, 0x140fd52d, 0x395412f8,
    0x2ba63360, 0x37e53ad0, 0x80700f1c, 0x7624ed0b, 0x703dc1ec, 0xb7366795,
    0xd6549d15, 0x66ce46d7, 0xd17abe76, 0xa448e0a0, 0x28f07c02, 0xc31249b7,
    0x6e9ed6ba, 0xeaa47f78, 0xbbcfffbd, 0xc507ca84, 0xe965f4da, 0x8e9f35da,
    0x6ad2aa44, 0x577452ac, 0xb5d674a7, 0x5461a46a, 0x6763152a, 0x9c12b7aa,
    0x12615927, 0x7b4fb118, 0xc351758d, 0x7e81687b, 0x5f52f0b3, 0x2d4254ed,
    0xd4c77271, 0x0431acab, 0xbef94aec, 0xfee994cd, 0x9c4d9e81, 0xed623730,
    0xcf8a21e8, 0x51917f0b, 0xa7a9b5d6, 0xb297adf8, 0xeed30431, 0x68cac921,
    0xf1b35d46, 0x7a430a36, 0x51194022, 0x9abca65e, 0x85ec70ba, 0x39aea8cc,
    0x737bae8b, 0x582924d5, 0x03098a5a, 0x92396b81, 0x18de2522, 0x745c1cb8,
    0xa1b8fe1d, 0x5db3c697, 0x29164f83, 0x97c16376, 0x8419224c, 0x21203b35,
    0x833ac0fe, 0xd966a19a, 0xaaf0b24f, 0x40fda998, 0xe7d52d71, 0x390896a8,
    0xcee6053f, 0xd0b0d300, 0xff99cbcc, 0x065e3d40
]

# Multiplication table for Turing using 0xd02b4367

_MULTAB = [
    0x00000000, 0xd02b4367, 0xed5686ce, 0x3d7dc5a9, 0x97ac41d1, 0x478702b6,
    0x7afac71f, 0xaad18478, 0x631582ef, 0xb33ec188, 0x8e430421, 0x5e684746,
    0xf4b9c33e, 0x24928059, 0x19ef45f0, 0xc9c40697, 0xc62a4993, 0x16010af4,
    0x2b7ccf5d, 0xfb578c3a, 0x51860842, 0x81ad4b25, 0xbcd08e8c, 0x6cfbcdeb,
    0xa53fcb7c, 0x7514881b, 0x48694db2, 0x98420ed5, 0x32938aad, 0xe2b8c9ca,
    0xdfc50c63, 0x0fee4f04, 0xc154926b, 0x117fd10c, 0x2c0214a5, 0xfc2957c2,
    0x56f8d3ba, 0x86d390dd, 0xbbae5574, 0x6b851613, 0xa2411084, 0x726a53e3,
    0x4f17964a, 0x9f3cd52d, 0x35ed5155, 0xe5c61232, 0xd8bbd79b, 0x089094fc,
    0x077edbf8, 0xd755989f, 0xea285d36, 0x3a031e51, 0x90d29a29, 0x40f9d94e,
    0x7d841ce7, 0xadaf5f80, 0x646b5917, 0xb4401a70, 0x893ddfd9, 0x59169cbe,
    0xf3c718c6, 0x23ec5ba1, 0x1e919e08, 0xcebadd6f, 0xcfa869d6, 0x1f832ab1,
    0x22feef18, 0xf2d5ac7f, 0x58042807, 0x882f6b60, 0xb552aec9, 0x6579edae,
    0xacbdeb39, 0x7c96a85e, 0x41eb6df7, 0x91c02e90, 0x3b11aae8, 0xeb3ae98f,
    0xd6472c26, 0x066c6f41, 0x09822045, 0xd9a96322, 0xe4d4a68b, 0x34ffe5ec,
    0x9e2e6194, 0x4e0522f3, 0x7378e75a, 0xa353a43d, 0x6a97a2aa, 0xbabce1cd,
    0x87c12464, 0x57ea6703, 0xfd3be37b, 0x2d10a01c, 0x106d65b5, 0xc04626d2,
    0x0efcfbbd, 0xded7b8da, 0xe3aa7d73, 0x33813e14, 0x9950ba6c, 0x497bf90b,
    0x74063ca2, 0xa42d7fc5, 0x6de97952, 0xbdc23a35, 0x80bfff9c, 0x5094bcfb,
    0xfa453883, 0x2a6e7be4, 0x1713be4d, 0xc738fd2a, 0xc8d6b22e, 0x18fdf149,
    0x258034e0, 0xf5ab7787, 0x5f7af3ff, 0x8f51b098, 0xb22c7531, 0x62073656,
    0xabc330c1, 0x7be873a6, 0x4695b60f, 0x96bef568, 0x3c6f7110, 0xec443277,
    0xd139f7de, 0x0112b4b9, 0xd31dd2e1, 0x03369186, 0x3e4b542f, 0xee601748,
    0x44b19330, 0x949ad057, 0xa9e715fe, 0x79cc5699, 0xb008500e, 0x60231369,
    0x5d5ed6c0, 0x8d7595a7, 0x27a411df, 0xf78f52b8, 0xcaf29711, 0x1ad9d476,
    0x15379b72, 0xc51cd815, 0xf8611dbc, 0x284a5edb, 0x829bdaa3, 0x52b099c4,
    0x6fcd5c6d, 0xbfe61f0a, 0x7622199d, 0xa6095afa, 0x9b749f53, 0x4b5fdc34,
    0xe18e584c, 0x31a51b2b, 0x0cd8de82, 0xdcf39de5, 0x1249408a, 0xc26203ed,
    0xff1fc644, 0x2f348523, 0x85e5015b, 0x55ce423c, 0x68b38795, 0xb898c4f2,
    0x715cc265, 0xa1778102, 0x9c0a44ab, 0x4c2107cc, 0xe6f083b4, 0x36dbc0d3,
    0x0ba6057a, 0xdb8d461d, 0xd4630919, 0x04484a7e, 0x39358fd7, 0xe91eccb0,
    0x43cf48c8, 0x93e40baf, 0xae99ce06, 0x7eb28d61, 0xb7768bf6, 0x675dc891,
    0x5a200d38, 0x8a0b4e5f, 0x20daca27, 0xf0f18940, 0xcd8c4ce9, 0x1da70f8e,
    0x1cb5bb37, 0xcc9ef850, 0xf1e33df9, 0x21c87e9e, 0x8b19fae6, 0x5b32b981,
    0x664f7c28, 0xb6643f4f, 0x7fa039d8, 0xaf8b7abf, 0x92f6bf16, 0x42ddfc71,
    0xe80c7809, 0x38273b6e, 0x055afec7, 0xd571bda0, 0xda9ff2a4, 0x0ab4b1c3,
    0x37c9746a, 0xe7e2370d, 0x4d33b375, 0x9d18f012, 0xa06535bb, 0x704e76dc,
    0xb98a704b, 0x69a1332c, 0x54dcf685, 0x84f7b5e2, 0x2e26319a, 0xfe0d72fd,
    0xc370b754, 0x135bf433, 0xdde1295c, 0x0dca6a3b, 0x30b7af92, 0xe09cecf5,
    0x4a4d688d, 0x9a662bea, 0xa71bee43, 0x7730ad24, 0xbef4abb3, 0x6edfe8d4,
    0x53a22d7d, 0x83896e1a, 0x2958ea62, 0xf973a905, 0xc40e6cac, 0x14252fcb,
    0x1bcb60cf, 0xcbe023a8, 0xf69de601, 0x26b6a566, 0x8c67211e, 0x5c4c6279,
    0x6131a7d0, 0xb11ae4b7, 0x78dee220, 0xa8f5a147, 0x958864ee, 0x45a32789,
    0xef72a3f1, 0x3f59e096, 0x0224253f, 0xd20f6658
]

# Basic _SBOX for Turing.

# This was generated by keying RC4 with the 11-character string "Alan
# Turing", and then ignoring 256 generated bytes. Then the current
# permutation was tested for nonlinearity, another byte generated, etc.,
# until a total of 10000 bytes had been generated. The best observed min
# nonlinearity was 104, which first occurred after 736 bytes had been
# generated. The corresponding state table is used in Turing. By happy
# coincidence it also has no fixed points (ie. _SBOX[x] != x for all x).

_SBOX = [
    0x61, 0x51, 0xeb, 0x19, 0xb9, 0x5d, 0x60, 0x38, 0x7c, 0xb2, 0x06, 0x12,
    0xc4, 0x5b, 0x16, 0x3b, 0x2b, 0x18, 0x83, 0xb0, 0x7f, 0x75, 0xfa, 0xa0,
    0xe9, 0xdd, 0x6d, 0x7a, 0x6b, 0x68, 0x2d, 0x49, 0xb5, 0x1c, 0x90, 0xf7,
    0xed, 0x9f, 0xe8, 0xce, 0xae, 0x77, 0xc2, 0x13, 0xfd, 0xcd, 0x3e, 0xcf,
    0x37, 0x6a, 0xd4, 0xdb, 0x8e, 0x65, 0x1f, 0x1a, 0x87, 0xcb, 0x40, 0x15,
    0x88, 0x0d, 0x35, 0xb3, 0x11, 0x0f, 0xd0, 0x30, 0x48, 0xf9, 0xa8, 0xac,
    0x85, 0x27, 0x0e, 0x8a, 0xe0, 0x50, 0x64, 0xa7, 0xcc, 0xe4, 0xf1, 0x98,
    0xff, 0xa1, 0x04, 0xda, 0xd5, 0xbc, 0x1b, 0xbb, 0xd1, 0xfe, 0x31, 0xca,
    0xba, 0xd9, 0x2e, 0xf3, 0x1d, 0x47, 0x4a, 0x3d, 0x71, 0x4c, 0xab, 0x7d,
    0x8d, 0xc7, 0x59, 0xb8, 0xc1, 0x96, 0x1e, 0xfc, 0x44, 0xc8, 0x7b, 0xdc,
    0x5c, 0x78, 0x2a, 0x9d, 0xa5, 0xf0, 0x73, 0x22, 0x89, 0x05, 0xf4, 0x07,
    0x21, 0x52, 0xa6, 0x28, 0x9a, 0x92, 0x69, 0x8f, 0xc5, 0xc3, 0xf5, 0xe1,
    0xde, 0xec, 0x09, 0xf2, 0xd3, 0xaf, 0x34, 0x23, 0xaa, 0xdf, 0x7e, 0x82,
    0x29, 0xc0, 0x24, 0x14, 0x03, 0x32, 0x4e, 0x39, 0x6f, 0xc6, 0xb1, 0x9b,
    0xea, 0x72, 0x79, 0x41, 0xd8, 0x26, 0x6c, 0x5e, 0x2c, 0xb4, 0xa2, 0x53,
    0x57, 0xe2, 0x9c, 0x86, 0x54, 0x95, 0xb6, 0x80, 0x8c, 0x36, 0x67, 0xbd,
    0x08, 0x93, 0x2f, 0x99, 0x5a, 0xf8, 0x3a, 0xd7, 0x56, 0x84, 0xd2, 0x01,
    0xf6, 0x66, 0x4d, 0x55, 0x8b, 0x0c, 0x0b, 0x46, 0xb7, 0x3c, 0x45, 0x91,
    0xa4, 0xe3, 0x70, 0xd6, 0xfb, 0xe6, 0x10, 0xa9, 0xc9, 0x00, 0x9e, 0xe7,
    0x4f, 0x76, 0x25, 0x3f, 0x5f, 0xa3, 0x33, 0x20, 0x02, 0xef, 0x62, 0x74,
    0xee, 0x17, 0x81, 0x42, 0x58, 0x0a, 0x4b, 0x63, 0xe5, 0xbe, 0x6e, 0xad,
    0xbf, 0x43, 0x94, 0x97
]

_MAXKEY = 32      # bytes
_MAXKIV = 48      # bytes
_LFSRLEN = 17     # words

def _getbyte(x, i):
    """ The ith byte of x """
    return (x >> (24 - 8 * i)) & 0xff

def _rotl(w, x):
    """ Rotate w left x bits """
    return (w << x) | (w >> (32 - x))

def _fixed_strans(w):
    """ Reversible transformation of a word, based on the S-boxes """
    b = _SBOX[_getbyte(w, 0)]
    w = ((w ^       _QBOX[b])      & 0x00ffffff) | (b << 24)
    b = _SBOX[_getbyte(w, 1)]
    w = ((w ^ _rotl(_QBOX[b], 8))  & 0xff00ffff) | (b << 16)
    b = _SBOX[_getbyte(w, 2)]
    w = ((w ^ _rotl(_QBOX[b], 16)) & 0xffff00ff) | (b << 8)
    b = _SBOX[_getbyte(w, 3)]
    w = ((w ^ _rotl(_QBOX[b], 24)) & 0xffffff00) | b
    return w

def _mixwords(w):
    """ Pseudo-Hadamard Transform """
    total = sum(w)
    return [(i + total) & 0xffffffff for i in w[:-1] + [0]]

class KeyLengthError(Exception):
    pass

class IVLengthError(Exception):
    pass

class Turing(object):
    def __init__(self, key=None, iv=None):
        self.sbox = [[], [], [], []]  # precalculated S-boxes
        self.index = 0

        if key:
            self.setkey(key)
            if iv:
                self.loadiv(iv)

    def _strans(self, w, b):
        """ Push a word through the keyed S-boxes """
        return (self.sbox[0][_getbyte(w, b)] ^
                self.sbox[1][_getbyte(w, (1 + b) & 3)] ^
                self.sbox[2][_getbyte(w, (2 + b) & 3)] ^
                self.sbox[3][_getbyte(w, (3 + b) & 3)])

    def setkey(self, key):
        """ Key the cipher.
            Table version; gathers words, mixes them, saves them.
            Then compiles lookup tables for the keyed S-boxes.

        """
        keylength = len(key)
        if keylength & 3 or keylength > _MAXKEY:
            raise KeyLengthError
        fmt = '>%dL' % (keylength / 4)
        self.mkey = _mixwords([_fixed_strans(n)
                               for n in struct.unpack(fmt, key)])

        # build S-box lookup tables
        for l, m in enumerate(self.sbox):
            sh1 = 8 * l
            sh2 = 24 - sh1
            mask = (0xff << sh2) ^ 0xffffffff
            for j in xrange(256):
                w = 0
                k = j
                for i, key in enumerate(self.mkey):
                    k = _SBOX[_getbyte(key, l) ^ k]
                    w ^= _rotl(_QBOX[k], i + sh1)
                m.append( (w & mask) | (k << sh2) )

    def loadiv(self, iv):
        """ Load the Initialization Vector.
            Actually, this fills the LFSR, with IV, key, length, and
            more. IV goes through the fixed S-box, key is premixed, the
            rest go through the keyed S-boxes.

        """
        ivlength, klength = len(iv), len(self.mkey)
        # check args
        if ivlength & 3 or (ivlength + 4 * klength) > _MAXKIV:
            raise IVLengthError
        # first copy in the IV, mixing as we go
        fmt = '>%dL' % (ivlength / 4)
        lfsr = [_fixed_strans(n) for n in struct.unpack(fmt, iv)]
        # now continue with the premixed key
        lfsr.extend(self.mkey)
        # now the length-dependent word
        lfsr.append( (klength << 4) | (ivlength >> 2) | 0x01020300 )
        # ... and fill the rest of the register
        j = 0
        while len(lfsr) < _LFSRLEN:
            lfsr.append(self._strans(lfsr[j] + lfsr[-1], 0))
            j += 1
        # finally mix all the words
        self.lfsr = _mixwords(lfsr)

    def _step(self, n=1):
        """ Step the LFSR """
        while n:
            z = self.index % _LFSRLEN
            self.lfsr[z] = (self.lfsr[(z + 15) % _LFSRLEN] ^
                            self.lfsr[(z + 4) % _LFSRLEN] ^
                          ((self.lfsr[z] & 0xffffff) << 8) ^
                   _MULTAB[(self.lfsr[z] >> 24)])
            self.index += 1
            n -= 1

    def _round(self):
        """ A single round """
        self._step()
        things = _mixwords([self.lfsr[(self.index + n) % _LFSRLEN]
                            for n in (16, 13, 6, 1, 0)])
        things = _mixwords([self._strans(i, n)
                            for i, n in izip(things, (0, 1, 2, 3, 0))])
        self._step(3)
        things = [(i + self.lfsr[(self.index + n) % _LFSRLEN]) & 0xffffffff
                  for i, n in izip(things, (14, 12, 8, 1, 0))]
        self._step()
        return struct.pack('>5L', *things)

    def gen(self, skip, length):
        """ Generate length characters of output, skipping the first
            skip characters.

        """
        while skip > 20:
            self._step(5)
            skip -= 20
        buf = ''
        while len(buf) < length + skip:
            buf += self._round()
        return buf[skip:length + skip]

    def crypt(self, source, skip=0):
        """ Return a transformed (encrypted or decrypted) version of the
            source string, skipping the first skip bytes of the Turing
            data.

        """
        xor_data = self.gen(skip, len(source))
        fmt = '%dB' % len(source)
        d2 = struct.unpack(fmt, source)
        x2 = struct.unpack(fmt, xor_data)
        return struct.pack(fmt, *(a ^ b for a, b in izip(d2, x2)))
