import unittest
import warnings

from HPOlibConfigSpace.hyperparameters import Constant, \
    UniformFloatHyperparameter, NormalFloatHyperparameter, \
    UniformIntegerHyperparameter, NormalIntegerHyperparameter, \
    CategoricalHyperparameter
from HPOlibConfigSpace.conditions import EqualsCondition, NotEqualsCondition,\
    InCondition, AndConjunction, OrConjunction

class TestConditions(unittest.TestCase):
    # TODO: return only copies of the objects!
    def test_equals_condition(self):
        hp1 = CategoricalHyperparameter("parent", [0, 1])
        hp2 = UniformIntegerHyperparameter("child", 0, 10)
        cond = EqualsCondition(hp2, hp1, 0)
        cond_ = EqualsCondition(hp2, hp1, 0)

        # Test invalid conditions:
        self.assertRaisesRegexp(ValueError, "Argument 'parent' is not an "
                                "instance of HPOlibConfigSpace.hyperparameter."
                                "Hyperparameter.", EqualsCondition, hp2,
                                "parent", 0)
        self.assertRaisesRegexp(ValueError, "Argument 'child' is not an "
                                "instance of HPOlibConfigSpace.hyperparameter."
                                "Hyperparameter.", EqualsCondition, "child",
                                hp1, 0)
        self.assertRaisesRegexp(ValueError, "The child and parent hyperparameter "
                                "must be different hyperparameters.",
                                EqualsCondition, hp1, hp1, 0)

        self.assertEqual(cond, cond_)

        cond_reverse = EqualsCondition(hp1, hp2, 0)
        self.assertNotEqual(cond, cond_reverse)

        self.assertNotEqual(cond, dict())

        self.assertEqual("child | parent == 0", str(cond))

    def test_equals_condition_illegal_value(self):
        epsilon = UniformFloatHyperparameter("epsilon", 1e-5, 1e-1,
                                             default=1e-4, log=True)
        loss = CategoricalHyperparameter("loss",
            ["hinge", "log", "modified_huber", "squared_hinge", "perceptron"],
            default="hinge")
        self.assertRaisesRegexp(ValueError, "Hyperparameter 'epsilon' is "
                                "conditional on the illegal value 'huber' of "
                                "its parent hyperparameter 'loss'",
            EqualsCondition, epsilon, loss, "huber")

    def test_not_equals_condition(self):
        hp1 = CategoricalHyperparameter("parent", [0, 1])
        hp2 = UniformIntegerHyperparameter("child", 0, 10)
        cond = NotEqualsCondition(hp2, hp1, 0)
        cond_ = NotEqualsCondition(hp2, hp1, 0)
        self.assertEqual(cond, cond_)

        cond_reverse = NotEqualsCondition(hp1, hp2, 0)
        self.assertNotEqual(cond, cond_reverse)

        self.assertNotEqual(cond, dict())

        self.assertEqual("child | parent != 0", str(cond))

    def test_not_equals_condition_illegal_value(self):
        epsilon = UniformFloatHyperparameter("epsilon", 1e-5, 1e-1,
                                             default=1e-4, log=True)
        loss = CategoricalHyperparameter("loss",
                                         ["hinge", "log", "modified_huber",
                                          "squared_hinge", "perceptron"],
                                         default="hinge")
        self.assertRaisesRegexp(ValueError, "Hyperparameter 'epsilon' is "
                                            "conditional on the illegal value 'huber' of "
                                            "its parent hyperparameter 'loss'",
                                NotEqualsCondition, epsilon, loss, "huber")

    def test_in_condition(self):
        hp1 = CategoricalHyperparameter("parent", range(0, 11))
        hp2 = UniformIntegerHyperparameter("child", 0, 10)
        cond = InCondition(hp2, hp1, [0, 1, 2, 3, 4, 5])
        cond_ = InCondition(hp2, hp1, [0, 1, 2, 3, 4, 5])
        self.assertEqual(cond, cond_)

        cond_reverse = InCondition(hp1, hp2, [0, 1, 2, 3, 4, 5])
        self.assertNotEqual(cond, cond_reverse)

        self.assertNotEqual(cond, dict())

        self.assertEqual("child | parent in {0, 1, 2, 3, 4, 5}", str(cond))

    def test_in_condition_illegal_value(self):
        epsilon = UniformFloatHyperparameter("epsilon", 1e-5, 1e-1,
                                             default=1e-4, log=True)
        loss = CategoricalHyperparameter("loss",
                                         ["hinge", "log", "modified_huber",
                                          "squared_hinge", "perceptron"],
                                         default="hinge")
        self.assertRaisesRegexp(ValueError, "Hyperparameter 'epsilon' is "
                                            "conditional on the illegal value 'huber' of "
                                            "its parent hyperparameter 'loss'",
                                InCondition, epsilon, loss, ["huber", "log"])

    def test_and_conjunction(self):
        self.assertRaises(TypeError, AndConjunction, "String1", "String2")

        hp1 = CategoricalHyperparameter("input1", [0, 1])
        hp2 = CategoricalHyperparameter("input2", [0, 1])
        hp3 = CategoricalHyperparameter("input3", [0, 1])
        hp4 = Constant("And", "True")
        cond1 = EqualsCondition(hp4, hp1, 1)

        # Only one condition in an AndConjunction!
        self.assertRaises(ValueError, AndConjunction, cond1)

        cond2 = EqualsCondition(hp4, hp2, 1)
        cond3 = EqualsCondition(hp4, hp3, 1)

        andconj1 = AndConjunction(cond1, cond2)
        andconj1_ = AndConjunction(cond1, cond2)
        self.assertEqual(andconj1, andconj1_)

        andconj2 = AndConjunction(cond2, cond3)
        self.assertNotEqual(andconj1, andconj2)

        andconj3 = AndConjunction(cond1, cond2, cond3)
        self.assertEqual("(And | input1 == 1 && And | input2 == 1 && And | "
                         "input3 == 1)", str(andconj3))

        # Test __eq__
        self.assertNotEqual(andconj1, andconj3)
        self.assertNotEqual(andconj1, "String")


    def test_or_conjunction(self):
        self.assertRaises(TypeError, AndConjunction, "String1", "String2")

        hp1 = CategoricalHyperparameter("input1", [0, 1])
        hp2 = CategoricalHyperparameter("input2", [0, 1])
        hp3 = CategoricalHyperparameter("input3", [0, 1])
        hp4 = Constant("Or", "True")
        cond1 = EqualsCondition(hp4, hp1, 1)

        self.assertRaises(ValueError, OrConjunction, cond1)

        cond2 = EqualsCondition(hp4, hp2, 1)
        cond3 = EqualsCondition(hp4, hp3, 1)

        andconj1 = OrConjunction(cond1, cond2)
        andconj1_ = OrConjunction(cond1, cond2)
        self.assertEqual(andconj1, andconj1_)

        andconj2 = OrConjunction(cond2, cond3)
        self.assertNotEqual(andconj1, andconj2)

        andconj3 = OrConjunction(cond1, cond2, cond3)
        self.assertEqual("(Or | input1 == 1 || Or | input2 == 1 || Or | "
                         "input3 == 1)", str(andconj3))

    def test_nested_conjunctions(self):
        hp1 = CategoricalHyperparameter("input1", [0, 1])
        hp2 = CategoricalHyperparameter("input2", [0, 1])
        hp3 = CategoricalHyperparameter("input3", [0, 1])
        hp4 = CategoricalHyperparameter("input4", [0, 1])
        hp5 = CategoricalHyperparameter("input5", [0, 1])
        hp6 = Constant("AND", "True")

        cond1 = EqualsCondition(hp6, hp1, 1)
        cond2 = EqualsCondition(hp6, hp2, 1)
        cond3 = EqualsCondition(hp6, hp3, 1)
        cond4 = EqualsCondition(hp6, hp4, 1)
        cond5 = EqualsCondition(hp6, hp5, 1)

        conj1 = AndConjunction(cond1, cond2)
        conj2 = OrConjunction(conj1, cond3)
        conj3 = AndConjunction(conj2, cond4, cond5)

        # TODO: this does not look nice, And should depend on a large
        # conjunction, there should not be many ANDs inside this string!
        self.assertEqual("(((AND | input1 == 1 && AND | input2 == 1) || AND | "
                         "input3 == 1) && AND | input4 == 1 && AND | input5 "
                         "== 1)", str(conj3))

    def test_all_components_have_the_same_child(self):
        hp1 = CategoricalHyperparameter("input1", [0, 1])
        hp2 = CategoricalHyperparameter("input2", [0, 1])
        hp3 = CategoricalHyperparameter("input3", [0, 1])
        hp4 = CategoricalHyperparameter("input4", [0, 1])
        hp5 = CategoricalHyperparameter("input5", [0, 1])
        hp6 = Constant("AND", "True")

        cond1 = EqualsCondition(hp1, hp2, 1)
        cond2 = EqualsCondition(hp1, hp3, 1)
        cond3 = EqualsCondition(hp1, hp4, 1)
        cond4 = EqualsCondition(hp6, hp4, 1)
        cond5 = EqualsCondition(hp6, hp5, 1)

        AndConjunction(cond1, cond2, cond3)
        AndConjunction(cond4, cond5)
        self.assertRaisesRegexp(ValueError,
                                "All Conjunctions and Conditions must have "
                                "the same child.", AndConjunction, cond1, cond4)

    def test_condition_from_cryptominisat(self):
        parent = CategoricalHyperparameter('blkrest', ['0', '1'], default='1')
        child = UniformIntegerHyperparameter('blkrestlen', 2000, 10000,
                                             log=True)
        condition = EqualsCondition(child, parent, '1')
        self.assertFalse(condition.evaluate(dict(blkrest='0')))
        self.assertTrue(condition.evaluate(dict(blkrest='1')))

