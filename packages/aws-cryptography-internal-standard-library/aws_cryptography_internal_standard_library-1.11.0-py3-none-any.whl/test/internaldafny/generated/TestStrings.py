import sys
from typing import Callable, Any, TypeVar, NamedTuple
from math import floor
from itertools import count

import module_ as module_
import _dafny as _dafny
import System_ as System_
import smithy_dafny_standard_library.internaldafny.generated.Wrappers as Wrappers
import smithy_dafny_standard_library.internaldafny.generated.Relations as Relations
import smithy_dafny_standard_library.internaldafny.generated.Seq_MergeSort as Seq_MergeSort
import smithy_dafny_standard_library.internaldafny.generated.Math as Math
import smithy_dafny_standard_library.internaldafny.generated.Seq as Seq
import smithy_dafny_standard_library.internaldafny.generated.BoundedInts as BoundedInts
import smithy_dafny_standard_library.internaldafny.generated.Unicode as Unicode
import smithy_dafny_standard_library.internaldafny.generated.Functions as Functions
import smithy_dafny_standard_library.internaldafny.generated.Utf8EncodingForm as Utf8EncodingForm
import smithy_dafny_standard_library.internaldafny.generated.Utf16EncodingForm as Utf16EncodingForm
import smithy_dafny_standard_library.internaldafny.generated.UnicodeStrings as UnicodeStrings
import smithy_dafny_standard_library.internaldafny.generated.FileIO as FileIO
import smithy_dafny_standard_library.internaldafny.generated.GeneralInternals as GeneralInternals
import smithy_dafny_standard_library.internaldafny.generated.MulInternalsNonlinear as MulInternalsNonlinear
import smithy_dafny_standard_library.internaldafny.generated.MulInternals as MulInternals
import smithy_dafny_standard_library.internaldafny.generated.Mul as Mul
import smithy_dafny_standard_library.internaldafny.generated.ModInternalsNonlinear as ModInternalsNonlinear
import smithy_dafny_standard_library.internaldafny.generated.DivInternalsNonlinear as DivInternalsNonlinear
import smithy_dafny_standard_library.internaldafny.generated.ModInternals as ModInternals
import smithy_dafny_standard_library.internaldafny.generated.DivInternals as DivInternals
import smithy_dafny_standard_library.internaldafny.generated.DivMod as DivMod
import smithy_dafny_standard_library.internaldafny.generated.Power as Power
import smithy_dafny_standard_library.internaldafny.generated.Logarithm as Logarithm
import smithy_dafny_standard_library.internaldafny.generated.StandardLibraryInterop as StandardLibraryInterop
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_UInt as StandardLibrary_UInt
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_MemoryMath as StandardLibrary_MemoryMath
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_Sequence as StandardLibrary_Sequence
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_String as StandardLibrary_String
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary as StandardLibrary
import smithy_dafny_standard_library.internaldafny.generated.UUID as UUID
import smithy_dafny_standard_library.internaldafny.generated.UTF8 as UTF8
import smithy_dafny_standard_library.internaldafny.generated.OsLang as OsLang
import smithy_dafny_standard_library.internaldafny.generated.Time as Time
import smithy_dafny_standard_library.internaldafny.generated.Streams as Streams
import smithy_dafny_standard_library.internaldafny.generated.Sorting as Sorting
import smithy_dafny_standard_library.internaldafny.generated.SortedSets as SortedSets
import smithy_dafny_standard_library.internaldafny.generated.HexStrings as HexStrings
import smithy_dafny_standard_library.internaldafny.generated.GetOpt as GetOpt
import smithy_dafny_standard_library.internaldafny.generated.FloatCompare as FloatCompare
import smithy_dafny_standard_library.internaldafny.generated.ConcurrentCall as ConcurrentCall
import smithy_dafny_standard_library.internaldafny.generated.Base64 as Base64
import smithy_dafny_standard_library.internaldafny.generated.Base64Lemmas as Base64Lemmas
import smithy_dafny_standard_library.internaldafny.generated.Actions as Actions
import smithy_dafny_standard_library.internaldafny.generated.DafnyLibraries as DafnyLibraries
import TestUUID as TestUUID
import TestUTF8 as TestUTF8
import TestTime as TestTime

# Module: TestStrings

class default__:
    def  __init__(self):
        pass

    @staticmethod
    def TestHasSubStringPositive():
        d_0_actual_: Wrappers.Option
        out0_: Wrappers.Option
        out0_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("Koda is a Dog."), _dafny.Seq("Koda"))
        d_0_actual_ = out0_
        if not((d_0_actual_) == (Wrappers.Option_Some(0))):
            raise _dafny.HaltException("test/TestString.dfy(19,4): " + _dafny.string_of(_dafny.Seq("'Koda' is in 'Koda is a Dog.' at index 0, but HasSubString does not think so")))
        out1_: Wrappers.Option
        out1_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("Koda is a Dog."), _dafny.Seq("Koda is a Dog."))
        d_0_actual_ = out1_
        if not((d_0_actual_) == (Wrappers.Option_Some(0))):
            raise _dafny.HaltException("test/TestString.dfy(21,4): " + _dafny.string_of(_dafny.Seq("'Koda is a Dog.' is in 'Koda is a Dog.' at index 0, but HasSubString does not think so")))
        out2_: Wrappers.Option
        out2_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("Koda is a Dog."), _dafny.Seq("Dog."))
        d_0_actual_ = out2_
        if not((d_0_actual_) == (Wrappers.Option_Some(10))):
            raise _dafny.HaltException("test/TestString.dfy(23,4): " + _dafny.string_of(_dafny.Seq("'Dog.' is in 'Koda is a Dog.' at index 10, but HasSubString does not think so")))
        out3_: Wrappers.Option
        out3_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("Koda is a Dog."), _dafny.Seq("."))
        d_0_actual_ = out3_
        if not((d_0_actual_) == (Wrappers.Option_Some(13))):
            raise _dafny.HaltException("test/TestString.dfy(25,4): " + _dafny.string_of(_dafny.Seq("'.' is in 'Koda is a Dog.' at index 13, but HasSubString does not think so")))
        out4_: Wrappers.Option
        out4_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("Koda is a Dog."), _dafny.Seq(""))
        d_0_actual_ = out4_
        if not((d_0_actual_) == (Wrappers.Option_Some(0))):
            raise _dafny.HaltException("test/TestString.dfy(27,4): " + _dafny.string_of(_dafny.Seq("The empty string is in 'Koda is a Dog.' at index 0, but HasSubString does not think so")))

    @staticmethod
    def TestHasSubStringNegative():
        d_0_actual_: Wrappers.Option
        out0_: Wrappers.Option
        out0_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("Robbie is a Dog."), _dafny.Seq("Koda"))
        d_0_actual_ = out0_
        if not((d_0_actual_) == (Wrappers.Option_None())):
            raise _dafny.HaltException("test/TestString.dfy(33,4): " + _dafny.string_of(_dafny.Seq("'Robbie is a Dog.' does not contain Koda")))
        out1_: Wrappers.Option
        out1_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("\t"), _dafny.Seq(" "))
        d_0_actual_ = out1_
        if not((d_0_actual_) == (Wrappers.Option_None())):
            raise _dafny.HaltException("test/TestString.dfy(35,4): " + _dafny.string_of(_dafny.Seq("A tab is not a space")))
        out2_: Wrappers.Option
        out2_ = StandardLibrary_String.default__.HasSubString(_dafny.Seq("large"), _dafny.Seq("larger"))
        d_0_actual_ = out2_
        if not((d_0_actual_) == (Wrappers.Option_None())):
            raise _dafny.HaltException("test/TestString.dfy(37,4): " + _dafny.string_of(_dafny.Seq("Needle larger than haystack")))

    @staticmethod
    def TestFileIO():
        d_0_valueOrError0_: Wrappers.Result = Wrappers.Result.default(_dafny.defaults.tuple())()
        out0_: Wrappers.Result
        out0_ = FileIO.default__.WriteBytesToFile(_dafny.Seq("MyFile"), _dafny.Seq([1, 2, 3, 4, 5]))
        d_0_valueOrError0_ = out0_
        if not(not((d_0_valueOrError0_).IsFailure())):
            raise _dafny.HaltException("test/TestString.dfy(42,13): " + _dafny.string_of(d_0_valueOrError0_))
        d_1_x_: tuple
        d_1_x_ = (d_0_valueOrError0_).Extract()
        d_2_valueOrError1_: Wrappers.Result = Wrappers.Result.default(_dafny.defaults.tuple())()
        out1_: Wrappers.Result
        out1_ = FileIO.default__.AppendBytesToFile(_dafny.Seq("MyFile"), _dafny.Seq([6, 7, 8, 9, 10]))
        d_2_valueOrError1_ = out1_
        if not(not((d_2_valueOrError1_).IsFailure())):
            raise _dafny.HaltException("test/TestString.dfy(43,9): " + _dafny.string_of(d_2_valueOrError1_))
        d_1_x_ = (d_2_valueOrError1_).Extract()
        d_3_valueOrError2_: Wrappers.Result = Wrappers.Result.default(_dafny.defaults.tuple())()
        out2_: Wrappers.Result
        out2_ = FileIO.default__.AppendBytesToFile(_dafny.Seq("MyFile"), _dafny.Seq([11, 12, 13, 14, 15]))
        d_3_valueOrError2_ = out2_
        if not(not((d_3_valueOrError2_).IsFailure())):
            raise _dafny.HaltException("test/TestString.dfy(44,9): " + _dafny.string_of(d_3_valueOrError2_))
        d_1_x_ = (d_3_valueOrError2_).Extract()
        d_4_valueOrError3_: Wrappers.Result = Wrappers.Result.default(_dafny.Seq)()
        out3_: Wrappers.Result
        out3_ = FileIO.default__.ReadBytesFromFile(_dafny.Seq("MyFile"))
        d_4_valueOrError3_ = out3_
        if not(not((d_4_valueOrError3_).IsFailure())):
            raise _dafny.HaltException("test/TestString.dfy(45,13): " + _dafny.string_of(d_4_valueOrError3_))
        d_5_y_: _dafny.Seq
        d_5_y_ = (d_4_valueOrError3_).Extract()
        if not((d_5_y_) == (_dafny.Seq([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))):
            raise _dafny.HaltException("test/TestString.dfy(46,4): " + _dafny.string_of(_dafny.Seq("expectation violation")))
        d_6_valueOrError4_: Wrappers.Result = Wrappers.Result.default(_dafny.defaults.tuple())()
        out4_: Wrappers.Result
        out4_ = FileIO.default__.WriteBytesToFile(_dafny.Seq("MyFile"), _dafny.Seq([1, 2, 3, 4, 5]))
        d_6_valueOrError4_ = out4_
        if not(not((d_6_valueOrError4_).IsFailure())):
            raise _dafny.HaltException("test/TestString.dfy(47,9): " + _dafny.string_of(d_6_valueOrError4_))
        d_1_x_ = (d_6_valueOrError4_).Extract()
        d_7_valueOrError5_: Wrappers.Result = Wrappers.Result.default(_dafny.Seq)()
        out5_: Wrappers.Result
        out5_ = FileIO.default__.ReadBytesFromFile(_dafny.Seq("MyFile"))
        d_7_valueOrError5_ = out5_
        if not(not((d_7_valueOrError5_).IsFailure())):
            raise _dafny.HaltException("test/TestString.dfy(48,9): " + _dafny.string_of(d_7_valueOrError5_))
        d_5_y_ = (d_7_valueOrError5_).Extract()
        if not((d_5_y_) == (_dafny.Seq([1, 2, 3, 4, 5]))):
            raise _dafny.HaltException("test/TestString.dfy(49,4): " + _dafny.string_of(_dafny.Seq("expectation violation")))

    @staticmethod
    def BadFilename():
        if ((OsLang.default__.GetOsShort()) == (_dafny.Seq("Windows"))) and ((OsLang.default__.GetLanguageShort()) == (_dafny.Seq("Dotnet"))):
            return _dafny.Seq("foo:bar:baz")
        elif True:
            return _dafny.Seq("/../../MyFile")

    @staticmethod
    def TestBadFileIO():
        d_0_x_: Wrappers.Result
        out0_: Wrappers.Result
        out0_ = FileIO.default__.WriteBytesToFile(default__.BadFilename(), _dafny.Seq([1, 2, 3, 4, 5]))
        d_0_x_ = out0_
        if not((d_0_x_).is_Failure):
            raise _dafny.HaltException("test/TestString.dfy(63,4): " + _dafny.string_of(_dafny.Seq("expectation violation")))

