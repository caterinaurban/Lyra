Search.setIndex({docnames:["abstract_domains","abstract_domains.liveness","abstract_domains.numerical","abstract_domains.traces","abstract_domains.usage","core","engine","engine.liveness","engine.traces","engine.usage","index","modules","semantics","semantics.usage"],envversion:53,filenames:["abstract_domains.rst","abstract_domains.liveness.rst","abstract_domains.numerical.rst","abstract_domains.traces.rst","abstract_domains.usage.rst","core.rst","engine.rst","engine.liveness.rst","engine.traces.rst","engine.usage.rst","index.rst","modules.rst","semantics.rst","semantics.usage.rst"],objects:{"":{abstract_domains:[0,0,0,"-"],core:[5,0,0,"-"],engine:[6,0,0,"-"],semantics:[12,0,0,"-"]},"abstract_domains.lattice":{BottomMixin:[0,1,1,""],BoundedLattice:[0,1,1,""],KindMixin:[0,1,1,""],Lattice:[0,1,1,""],TopMixin:[0,1,1,""]},"abstract_domains.lattice.BottomMixin":{bottom:[0,2,1,""],is_bottom:[0,2,1,""]},"abstract_domains.lattice.BoundedLattice":{bottom:[0,2,1,""],is_bottom:[0,2,1,""],is_top:[0,2,1,""],top:[0,2,1,""]},"abstract_domains.lattice.KindMixin":{Kind:[0,1,1,""],kind:[0,3,1,""]},"abstract_domains.lattice.KindMixin.Kind":{BOTTOM:[0,3,1,""],DEFAULT:[0,3,1,""],TOP:[0,3,1,""]},"abstract_domains.lattice.Lattice":{big_join:[0,2,1,""],big_meet:[0,2,1,""],bottom:[0,2,1,""],is_bottom:[0,2,1,""],is_top:[0,2,1,""],join:[0,2,1,""],less_equal:[0,2,1,""],meet:[0,2,1,""],replace:[0,2,1,""],top:[0,2,1,""],widening:[0,2,1,""]},"abstract_domains.lattice.TopMixin":{is_top:[0,2,1,""],top:[0,2,1,""]},"abstract_domains.liveness":{liveness_domain:[1,0,0,"-"]},"abstract_domains.liveness.liveness_domain":{LivenessLattice:[1,1,1,""],LivenessState:[1,1,1,""]},"abstract_domains.liveness.liveness_domain.LivenessLattice":{Status:[1,1,1,""],_join:[1,2,1,""],_less_equal:[1,2,1,""],_meet:[1,2,1,""],_widening:[1,2,1,""],bottom:[1,2,1,""],element:[1,3,1,""],is_bottom:[1,2,1,""],is_top:[1,2,1,""],top:[1,2,1,""]},"abstract_domains.liveness.liveness_domain.LivenessLattice.Status":{Dead:[1,3,1,""],Live:[1,3,1,""]},"abstract_domains.liveness.liveness_domain.LivenessState":{_assign_variable:[1,2,1,""],_assume:[1,2,1,""],_output:[1,2,1,""],_substitute_variable:[1,2,1,""],enter_if:[1,2,1,""],enter_loop:[1,2,1,""],exit_if:[1,2,1,""],exit_loop:[1,2,1,""]},"abstract_domains.numerical":{dbm:[2,0,0,"-"],interval_domain:[2,0,0,"-"],linear_forms:[2,0,0,"-"],numerical:[2,0,0,"-"],octagon_domain:[2,0,0,"-"]},"abstract_domains.numerical.dbm":{CDBM:[2,1,1,""],IntegerCDBM:[2,1,1,""],nan2inf:[2,4,1,""]},"abstract_domains.numerical.dbm.CDBM":{close:[2,2,1,""],intersection:[2,2,1,""],items:[2,2,1,""],keys:[2,2,1,""],replace:[2,2,1,""],size:[2,3,1,""],strongly_closed:[2,3,1,""],tightly_closed:[2,3,1,""],union:[2,2,1,""],values:[2,2,1,""],zip:[2,2,1,""]},"abstract_domains.numerical.dbm.IntegerCDBM":{close:[2,2,1,""]},"abstract_domains.numerical.interval_domain":{Interval:[2,1,1,""],IntervalDomain:[2,1,1,""],IntervalLattice:[2,1,1,""]},"abstract_domains.numerical.interval_domain.Interval":{add:[2,2,1,""],empty:[2,2,1,""],interval:[2,3,1,""],lower:[2,3,1,""],mult:[2,2,1,""],negate:[2,2,1,""],set_empty:[2,2,1,""],sub:[2,2,1,""],upper:[2,3,1,""]},"abstract_domains.numerical.interval_domain.IntervalDomain":{Visitor:[2,1,1,""],enter_if:[2,2,1,""],enter_loop:[2,2,1,""],evaluate:[2,2,1,""],exit_if:[2,2,1,""],exit_loop:[2,2,1,""],forget:[2,2,1,""],get_bounds:[2,2,1,""],set_bounds:[2,2,1,""],set_interval:[2,2,1,""],set_lb:[2,2,1,""],set_ub:[2,2,1,""]},"abstract_domains.numerical.interval_domain.IntervalDomain.Visitor":{visit_VariableIdentifier:[2,2,1,""]},"abstract_domains.numerical.interval_domain.IntervalLattice":{Visitor:[2,1,1,""],evaluate:[2,5,1,""],is_bottom:[2,2,1,""],is_top:[2,2,1,""],top:[2,2,1,""]},"abstract_domains.numerical.interval_domain.IntervalLattice.Visitor":{generic_visit:[2,2,1,""],visit_BinaryArithmeticOperation:[2,2,1,""],visit_Input:[2,2,1,""],visit_Literal:[2,2,1,""],visit_UnaryArithmeticOperation:[2,2,1,""]},"abstract_domains.numerical.linear_forms":{InvalidFormError:[2,6,1,""],LinearForm:[2,1,1,""],SingleVarLinearForm:[2,1,1,""]},"abstract_domains.numerical.linear_forms.LinearForm":{Visitor:[2,1,1,""],interval:[2,3,1,""],var_summands:[2,3,1,""]},"abstract_domains.numerical.linear_forms.LinearForm.Visitor":{generic_visit:[2,2,1,""],visit_BinaryArithmeticOperation:[2,2,1,""],visit_Input:[2,2,1,""],visit_Literal:[2,2,1,""],visit_UnaryArithmeticOperation:[2,2,1,""],visit_VariableIdentifier:[2,2,1,""],visit_VariadicArithmeticOperation:[2,2,1,""]},"abstract_domains.numerical.linear_forms.SingleVarLinearForm":{"var":[2,3,1,""],var_sign:[2,3,1,""]},"abstract_domains.numerical.numerical":{NumericalMixin:[2,1,1,""]},"abstract_domains.numerical.numerical.NumericalMixin":{evaluate:[2,2,1,""],forget:[2,2,1,""],get_bounds:[2,2,1,""],set_bounds:[2,2,1,""]},"abstract_domains.numerical.octagon_domain":{OctagonDomain:[2,1,1,""],OctagonLattice:[2,1,1,""]},"abstract_domains.numerical.octagon_domain.OctagonDomain":{AssumeVisitor:[2,1,1,""],SmallerEqualConditionTransformer:[2,1,1,""],enter_if:[2,2,1,""],enter_loop:[2,2,1,""],exit_if:[2,2,1,""],exit_loop:[2,2,1,""]},"abstract_domains.numerical.octagon_domain.OctagonDomain.AssumeVisitor":{generic_visit:[2,2,1,""],visit_BinaryBooleanOperation:[2,2,1,""],visit_BinaryComparisonOperation:[2,2,1,""],visit_UnaryBooleanOperation:[2,2,1,""]},"abstract_domains.numerical.octagon_domain.OctagonDomain.SmallerEqualConditionTransformer":{ConditionSet:[2,1,1,""],generic_visit:[2,2,1,""],visit_BinaryComparisonOperation:[2,2,1,""]},"abstract_domains.numerical.octagon_domain.OctagonDomain.SmallerEqualConditionTransformer.ConditionSet":{Operator:[2,1,1,""],combine_conditions:[2,2,1,""],condition_to_octagon:[2,3,1,""],conditions:[2,3,1,""],octagons:[2,3,1,""]},"abstract_domains.numerical.octagon_domain.OctagonDomain.SmallerEqualConditionTransformer.ConditionSet.Operator":{JOIN:[2,3,1,""],MEET:[2,3,1,""]},"abstract_domains.numerical.octagon_domain.OctagonLattice":{binary_constraints_indices:[2,2,1,""],close:[2,2,1,""],dbm:[2,3,1,""],evaluate:[2,2,1,""],forget:[2,2,1,""],from_interval_domain:[2,2,1,""],get_bounds:[2,2,1,""],get_interval:[2,2,1,""],get_lb:[2,2,1,""],get_ub:[2,2,1,""],is_top:[2,2,1,""],lower_octagonal_constraint:[2,2,1,""],lower_ub:[2,2,1,""],raise_lb:[2,2,1,""],set_bounds:[2,2,1,""],set_interval:[2,2,1,""],set_lb:[2,2,1,""],set_octagonal_constraint:[2,2,1,""],set_ub:[2,2,1,""],switch_constraints:[2,2,1,""],to_interval_domain:[2,2,1,""],top:[2,2,1,""],variables:[2,3,1,""]},"abstract_domains.stack":{Stack:[0,1,1,""]},"abstract_domains.stack.Stack":{_join:[0,2,1,""],_less_equal:[0,2,1,""],_meet:[0,2,1,""],pop:[0,2,1,""],push:[0,2,1,""],stack:[0,3,1,""]},"abstract_domains.state":{State:[0,1,1,""]},"abstract_domains.state.State":{access_variable:[0,2,1,""],assign_variable:[0,2,1,""],assume:[0,2,1,""],enter_if:[0,2,1,""],enter_loop:[0,2,1,""],evaluate_literal:[0,2,1,""],exit_if:[0,2,1,""],exit_loop:[0,2,1,""],filter:[0,2,1,""],output:[0,2,1,""],result:[0,3,1,""],substitute_variable:[0,2,1,""]},"abstract_domains.store":{Store:[0,1,1,""]},"abstract_domains.store.Store":{_join:[0,2,1,""],_less_equal:[0,2,1,""],_meet:[0,2,1,""],bottom:[0,2,1,""],is_bottom:[0,2,1,""],is_top:[0,2,1,""],store:[0,3,1,""],top:[0,2,1,""],variables:[0,3,1,""]},"abstract_domains.traces":{traces_domain:[3,0,0,"-"]},"abstract_domains.traces.traces_domain":{BoolTracesState:[3,1,1,""],TvlTracesState:[3,1,1,""]},"abstract_domains.traces.traces_domain.BoolTracesState":{BoolTrace:[3,1,1,""],enter_if:[3,2,1,""],enter_loop:[3,2,1,""],exit_if:[3,2,1,""],exit_loop:[3,2,1,""],hyper:[3,3,1,""],sets:[3,3,1,""],traces:[3,3,1,""],variables:[3,3,1,""]},"abstract_domains.traces.traces_domain.BoolTracesState.BoolTrace":{evaluate:[3,2,1,""],replace:[3,2,1,""],test:[3,2,1,""],trace:[3,3,1,""],variety:[3,2,1,""]},"abstract_domains.traces.traces_domain.TvlTracesState":{TvlTrace:[3,1,1,""],enter_if:[3,2,1,""],enter_loop:[3,2,1,""],exit_if:[3,2,1,""],exit_loop:[3,2,1,""],hyper:[3,3,1,""],sets:[3,3,1,""],traces:[3,3,1,""],variables:[3,3,1,""]},"abstract_domains.traces.traces_domain.TvlTracesState.TvlTrace":{evaluate:[3,2,1,""],replace:[3,2,1,""],test:[3,2,1,""],trace:[3,3,1,""],variety:[3,2,1,""]},"abstract_domains.usage":{stack:[4,0,0,"-"],store:[4,0,0,"-"],test_usedListStartLattice:[4,0,0,"-"],used:[4,0,0,"-"],used_liststart:[4,0,0,"-"]},"abstract_domains.usage.stack":{UsedStack:[4,1,1,""]},"abstract_domains.usage.stack.UsedStack":{enter_if:[4,2,1,""],enter_loop:[4,2,1,""],exit_if:[4,2,1,""],exit_loop:[4,2,1,""],pop:[4,2,1,""],push:[4,2,1,""]},"abstract_domains.usage.store":{UsedStore:[4,1,1,""]},"abstract_domains.usage.store.UsedStore":{combine:[4,2,1,""],descend:[4,2,1,""],enter_if:[4,2,1,""],enter_loop:[4,2,1,""],exit_if:[4,2,1,""],exit_loop:[4,2,1,""]},"abstract_domains.usage.test_usedListStartLattice":{TestUsedListStartLattice:[4,1,1,""]},"abstract_domains.usage.test_usedListStartLattice.TestUsedListStartLattice":{test_combine:[4,2,1,""]},"abstract_domains.usage.used":{Used:[4,1,1,""],UsedLattice:[4,1,1,""]},"abstract_domains.usage.used.Used":{N:[4,3,1,""],O:[4,3,1,""],S:[4,3,1,""],U:[4,3,1,""]},"abstract_domains.usage.used.UsedLattice":{COMBINE:[4,3,1,""],DESCEND:[4,3,1,""],combine:[4,2,1,""],descend:[4,2,1,""],is_top:[4,2,1,""],top:[4,2,1,""],used:[4,3,1,""]},"abstract_domains.usage.used_liststart":{UsedListStartLattice:[4,1,1,""]},"abstract_domains.usage.used_liststart.UsedListStartLattice":{change_SU_to_O:[4,2,1,""],change_S_to_U:[4,2,1,""],closed:[4,3,1,""],closure:[4,2,1,""],combine:[4,2,1,""],descend:[4,2,1,""],is_top:[4,2,1,""],set_used_at:[4,2,1,""],suo:[4,3,1,""],top:[4,2,1,""],used_at:[4,2,1,""]},"core.cfg":{Basic:[5,1,1,""],Conditional:[5,1,1,""],ControlFlowGraph:[5,1,1,""],Edge:[5,1,1,""],Loop:[5,1,1,""],Node:[5,1,1,""],Unconditional:[5,1,1,""]},"core.cfg.Conditional":{condition:[5,3,1,""]},"core.cfg.ControlFlowGraph":{edges:[5,3,1,""],in_edges:[5,2,1,""],in_node:[5,3,1,""],nodes:[5,3,1,""],nodes_backward:[5,2,1,""],nodes_forward:[5,2,1,""],out_edges:[5,2,1,""],out_node:[5,3,1,""],predecessors:[5,2,1,""],successors:[5,2,1,""]},"core.cfg.Edge":{Kind:[5,1,1,""],kind:[5,3,1,""],source:[5,3,1,""],target:[5,3,1,""]},"core.cfg.Edge.Kind":{DEFAULT:[5,3,1,""],IF_IN:[5,3,1,""],IF_OUT:[5,3,1,""],LOOP_IN:[5,3,1,""],LOOP_OUT:[5,3,1,""]},"core.cfg.Node":{identifier:[5,3,1,""],size:[5,2,1,""],stmts:[5,3,1,""]},"core.expressions":{AttributeReference:[5,1,1,""],BinaryArithmeticOperation:[5,1,1,""],BinaryBooleanOperation:[5,1,1,""],BinaryComparisonOperation:[5,1,1,""],BinaryOperation:[5,1,1,""],Expression:[5,1,1,""],Identifier:[5,1,1,""],Index:[5,1,1,""],Input:[5,1,1,""],ListDisplay:[5,1,1,""],Literal:[5,1,1,""],Operation:[5,1,1,""],Slice:[5,1,1,""],UnaryArithmeticOperation:[5,1,1,""],UnaryBooleanOperation:[5,1,1,""],UnaryOperation:[5,1,1,""],VariableIdentifier:[5,1,1,""]},"core.expressions.AttributeReference":{attribute:[5,3,1,""],primary:[5,3,1,""]},"core.expressions.BinaryArithmeticOperation":{Operator:[5,1,1,""]},"core.expressions.BinaryArithmeticOperation.Operator":{Add:[5,3,1,""],Div:[5,3,1,""],Mult:[5,3,1,""],Sub:[5,3,1,""]},"core.expressions.BinaryBooleanOperation":{Operator:[5,1,1,""]},"core.expressions.BinaryBooleanOperation.Operator":{And:[5,3,1,""],Or:[5,3,1,""],Xor:[5,3,1,""]},"core.expressions.BinaryComparisonOperation":{Operator:[5,1,1,""]},"core.expressions.BinaryComparisonOperation.Operator":{Eq:[5,3,1,""],Gt:[5,3,1,""],GtE:[5,3,1,""],In:[5,3,1,""],Is:[5,3,1,""],IsNot:[5,3,1,""],Lt:[5,3,1,""],LtE:[5,3,1,""],NotEq:[5,3,1,""],NotIn:[5,3,1,""],reverse_operator:[5,2,1,""]},"core.expressions.BinaryOperation":{Operator:[5,1,1,""],left:[5,3,1,""],operator:[5,3,1,""],right:[5,3,1,""]},"core.expressions.Expression":{ids:[5,2,1,""],typ:[5,3,1,""]},"core.expressions.Identifier":{name:[5,3,1,""]},"core.expressions.Index":{index:[5,3,1,""],target:[5,3,1,""]},"core.expressions.ListDisplay":{items:[5,3,1,""]},"core.expressions.Literal":{val:[5,3,1,""]},"core.expressions.Slice":{lower:[5,3,1,""],step:[5,3,1,""],target:[5,3,1,""],upper:[5,3,1,""]},"core.expressions.UnaryArithmeticOperation":{Operator:[5,1,1,""]},"core.expressions.UnaryArithmeticOperation.Operator":{Add:[5,3,1,""],Sub:[5,3,1,""]},"core.expressions.UnaryBooleanOperation":{Operator:[5,1,1,""]},"core.expressions.UnaryBooleanOperation.Operator":{Neg:[5,3,1,""]},"core.expressions.UnaryOperation":{Operator:[5,1,1,""],expression:[5,3,1,""],operator:[5,3,1,""]},"core.expressions_tools":{Expander:[5,1,1,""],ExpanderCleanup:[5,1,1,""],ExpressionTransformer:[5,1,1,""],ExpressionVisitor:[5,1,1,""],NotFreeConditionTransformer:[5,1,1,""],Simplifier:[5,1,1,""],expand:[5,4,1,""],iter_child_exprs:[5,4,1,""],iter_fields:[5,4,1,""],make_condition_not_free:[5,4,1,""],simplify:[5,4,1,""],walk:[5,4,1,""]},"core.expressions_tools.Expander":{generic_visit:[5,2,1,""],visit_BinaryArithmeticOperation:[5,2,1,""],visit_UnaryArithmeticOperation:[5,2,1,""]},"core.expressions_tools.ExpanderCleanup":{visit_VariadicArithmeticOperation:[5,2,1,""]},"core.expressions_tools.ExpressionTransformer":{generic_visit:[5,2,1,""]},"core.expressions_tools.ExpressionVisitor":{finalize_result:[5,2,1,""],generic_visit:[5,2,1,""],run:[5,2,1,""],visit:[5,2,1,""]},"core.expressions_tools.NotFreeConditionTransformer":{visit_BinaryBooleanOperation:[5,2,1,""],visit_BinaryComparisonOperation:[5,2,1,""],visit_UnaryBooleanOperation:[5,2,1,""]},"core.expressions_tools.Simplifier":{finalize_result:[5,2,1,""],generic_visit:[5,2,1,""],visit_BinaryArithmeticOperation:[5,2,1,""],visit_Literal:[5,2,1,""],visit_UnaryArithmeticOperation:[5,2,1,""],visit_VariadicArithmeticOperation:[5,2,1,""]},"core.special_expressions":{VariadicArithmeticOperation:[5,1,1,""]},"core.special_expressions.VariadicArithmeticOperation":{operands:[5,3,1,""],operator:[5,3,1,""]},"core.statements":{Assignment:[5,1,1,""],Call:[5,1,1,""],IndexStmt:[5,1,1,""],ListDisplayStmt:[5,1,1,""],LiteralEvaluation:[5,1,1,""],ProgramPoint:[5,1,1,""],SliceStmt:[5,1,1,""],Statement:[5,1,1,""],VariableAccess:[5,1,1,""]},"core.statements.Assignment":{left:[5,3,1,""],right:[5,3,1,""]},"core.statements.Call":{arguments:[5,3,1,""],name:[5,3,1,""],typ:[5,3,1,""]},"core.statements.IndexStmt":{index:[5,3,1,""],target:[5,3,1,""]},"core.statements.ListDisplayStmt":{items:[5,3,1,""]},"core.statements.LiteralEvaluation":{literal:[5,3,1,""]},"core.statements.ProgramPoint":{column:[5,3,1,""],line:[5,3,1,""]},"core.statements.SliceStmt":{lower:[5,3,1,""],step:[5,3,1,""],target:[5,3,1,""],upper:[5,3,1,""]},"core.statements.Statement":{pp:[5,3,1,""]},"core.statements.VariableAccess":{"var":[5,3,1,""]},"core.utils":{copy_docstring:[5,4,1,""]},"engine.backward":{BackwardInterpreter:[6,1,1,""]},"engine.backward.BackwardInterpreter":{analyze:[6,2,1,""],semantics:[6,3,1,""]},"engine.forward":{ForwardInterpreter:[6,1,1,""]},"engine.forward.ForwardInterpreter":{analyze:[6,2,1,""]},"engine.interpreter":{Interpreter:[6,1,1,""]},"engine.interpreter.Interpreter":{analyze:[6,2,1,""],cfg:[6,3,1,""],result:[6,3,1,""],semantics:[6,3,1,""],widening:[6,3,1,""]},"engine.liveness":{liveness_analysis:[7,0,0,"-"]},"engine.liveness.liveness_analysis":{LivenessAnalysis:[7,1,1,""]},"engine.liveness.liveness_analysis.LivenessAnalysis":{interpreter:[7,2,1,""],state:[7,2,1,""]},"engine.result":{AnalysisResult:[6,1,1,""]},"engine.result.AnalysisResult":{cfg:[6,3,1,""],get_node_result:[6,2,1,""],result:[6,3,1,""],set_node_result:[6,2,1,""]},"engine.runner":{Runner:[6,1,1,""]},"engine.runner.Runner":{cfg:[6,3,1,""],interpreter:[6,2,1,""],main:[6,2,1,""],path:[6,3,1,""],render:[6,2,1,""],run:[6,2,1,""],state:[6,2,1,""],tree:[6,3,1,""]},"engine.traces":{traces_analysis:[8,0,0,"-"]},"engine.traces.traces_analysis":{BoolTracesAnalysis:[8,1,1,""],TvlTracesAnalysis:[8,1,1,""]},"engine.traces.traces_analysis.BoolTracesAnalysis":{interpreter:[8,2,1,""],state:[8,2,1,""]},"engine.traces.traces_analysis.TvlTracesAnalysis":{interpreter:[8,2,1,""],state:[8,2,1,""]},"engine.usage":{usage_analysis:[9,0,0,"-"]},"engine.usage.usage_analysis":{UsageAnalysis:[9,1,1,""]},"engine.usage.usage_analysis.UsageAnalysis":{interpreter:[9,2,1,""],state:[9,2,1,""]},"semantics.backward":{AssignmentSemantics:[12,1,1,""],BackwardSemantics:[12,1,1,""],DefaultBackwardSemantics:[12,1,1,""],UserDefinedCallSemantics:[12,1,1,""]},"semantics.backward.AssignmentSemantics":{assignment_semantics:[12,2,1,""]},"semantics.backward.UserDefinedCallSemantics":{user_defined_call_semantics:[12,2,1,""]},"semantics.forward":{AssignmentSemantics:[12,1,1,""],DefaultForwardSemantics:[12,1,1,""],ForwardSemantics:[12,1,1,""],UserDefinedCallSemantics:[12,1,1,""]},"semantics.forward.AssignmentSemantics":{assignment_semantics:[12,2,1,""]},"semantics.forward.UserDefinedCallSemantics":{user_defined_call_semantics:[12,2,1,""]},"semantics.semantics":{BuiltInCallSemantics:[12,1,1,""],CallSemantics:[12,1,1,""],DefaultSemantics:[12,1,1,""],ListSemantics:[12,1,1,""],LiteralEvaluationSemantics:[12,1,1,""],Semantics:[12,1,1,""],VariableAccessSemantics:[12,1,1,""],camel_to_snake:[12,4,1,""]},"semantics.semantics.BuiltInCallSemantics":{add_call_semantics:[12,2,1,""],and_call_semantics:[12,2,1,""],binary_operation:[12,2,1,""],bool_call_semantics:[12,2,1,""],div_call_semantics:[12,2,1,""],eq_call_semantics:[12,2,1,""],gt_call_semantics:[12,2,1,""],gte_call_semantics:[12,2,1,""],in_call_semantics:[12,2,1,""],input_call_semantics:[12,2,1,""],int_call_semantics:[12,2,1,""],is_call_semantics:[12,2,1,""],isnot_call_semantics:[12,2,1,""],lt_call_semantics:[12,2,1,""],lte_call_semantics:[12,2,1,""],mult_call_semantics:[12,2,1,""],not_call_semantics:[12,2,1,""],noteq_call_semantics:[12,2,1,""],notin_call_semantics:[12,2,1,""],or_call_semantics:[12,2,1,""],print_call_semantics:[12,2,1,""],sub_call_semantics:[12,2,1,""],uadd_call_semantics:[12,2,1,""],unary_operation:[12,2,1,""],usub_call_semantics:[12,2,1,""],xor_call_semantics:[12,2,1,""]},"semantics.semantics.CallSemantics":{call_semantics:[12,2,1,""]},"semantics.semantics.ListSemantics":{index_stmt_semantics:[12,2,1,""],list_display_stmt_semantics:[12,2,1,""],slice_stmt_semantics:[12,2,1,""]},"semantics.semantics.LiteralEvaluationSemantics":{literal_evaluation_semantics:[12,2,1,""]},"semantics.semantics.Semantics":{semantics:[12,2,1,""]},"semantics.semantics.VariableAccessSemantics":{variable_access_semantics:[12,2,1,""]},"semantics.usage":{usage_semantics:[13,0,0,"-"]},"semantics.usage.usage_semantics":{UsageSemantics:[13,1,1,""]},"semantics.usage.usage_semantics.UsageSemantics":{user_defined_call_semantics:[13,2,1,""]},abstract_domains:{lattice:[0,0,0,"-"],liveness:[1,0,0,"-"],numerical:[2,0,0,"-"],stack:[0,0,0,"-"],state:[0,0,0,"-"],store:[0,0,0,"-"],traces:[3,0,0,"-"],usage:[4,0,0,"-"]},core:{cfg:[5,0,0,"-"],expressions:[5,0,0,"-"],expressions_tools:[5,0,0,"-"],special_expressions:[5,0,0,"-"],statements:[5,0,0,"-"],utils:[5,0,0,"-"]},engine:{backward:[6,0,0,"-"],forward:[6,0,0,"-"],interpreter:[6,0,0,"-"],liveness:[7,0,0,"-"],result:[6,0,0,"-"],runner:[6,0,0,"-"],traces:[8,0,0,"-"],usage:[9,0,0,"-"]},semantics:{backward:[12,0,0,"-"],forward:[12,0,0,"-"],semantics:[12,0,0,"-"],usage:[13,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","function","Python function"],"5":["py","classmethod","Python class method"],"6":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:function","5":"py:classmethod","6":"py:exception"},terms:{"abstract":[2,4,5,11],"boolean":5,"case":[4,5],"class":[0,1,2,3,4,5,6,7,8,9,12,13],"default":[0,1,5,12],"enum":[0,1,2,4,5],"final":5,"float":[2,4],"function":[0,5,12],"int":[2,3,5,6],"return":[0,1,2,5,6,12],"true":2,"var":[0,2,5],And:5,For:5,One:2,The:[0,1,2,5],Used:4,Uses:5,_assign_vari:1,_assum:1,_field:5,_forwardref:[0,5],_join:[0,1],_less_equ:[0,1],_meet:[0,1],_output:1,_substitute_vari:1,_widen:1,about:[2,5],abstract_domain:[6,10,11,12,13],abstractli:2,access:[0,5,12],access_vari:0,actual:2,add:[0,2,5,12],add_call_semant:12,adding:5,addit:[4,12],adjac:2,adopt:5,agre:2,algorithm:2,all:[0,1,2,5],allow:5,alreadi:2,also:5,analysi:[0,1,4,6,12],analysisresult:6,analyz:[0,6],ancestor:5,and_call_semant:12,ani:[0,2,4],annot:4,anoth:0,appear:5,append:5,appli:5,arg:[2,5],argument:[0,5],arithmet:5,assign:[0,1,5,12],assign_vari:0,assignment_semant:12,assignmentsemant:12,assum:[0,1,2],assumevisitor:2,assumpt:[0,1],ast:5,attribut:5,attributerefer:5,backward:[6,12,13],backwardinterpret:6,backwardsemant:[6,12],bagnara:2,base:[0,1,2,3,4,5,6,7,8,9,12,13],basic:5,befor:[1,2,5,12],behavior:5,between:[0,1],big_join:0,big_meet:0,binari:[2,5],binary_constraints_indic:2,binary_oper:12,binaryarithmeticoper:[2,5],binarybooleanoper:[2,5],binarycomparisonoper:[2,5],binaryoper:[5,12],bitwis:5,block:6,bool:[0,1,2,3,4],bool_call_semant:12,booltrac:3,booltracesanalysi:8,booltracesst:3,both:2,bottom:[0,1,2],bottommixin:[0,2,4],bound:[0,1,2],boundedlattic:[0,3],built:12,builtincallsemant:12,calcul:2,call:[5,12,13],call_semant:12,caller:5,callsemant:12,camel_to_snak:12,camelcas:12,can:5,canon:2,care:5,cdbm:2,cfg:[5,6],chang:[4,5],change_s_to_u:4,change_su_to_o:4,child:5,classmethod:2,clean:5,close:[2,4],closur:[2,4],coher:2,collect:5,column:[2,5],combin:4,combine_condit:2,comparison:[0,5],comput:0,concaten:12,cond:2,condit:[0,1,2,4,5],condition_to_octagon:2,conditionset:2,consist:[0,2,4],constant:2,constraint:2,contain:2,content:10,context:5,contribut:2,control:[5,6],controlflowgraph:[5,6],convert:12,copi:5,copy_docstr:5,copy_loc:5,core:[0,1,2,3,4,6,10,11,12,13],correspond:0,cover:4,ctx:5,current:[0,1,5],custom:5,data:5,dbm:2,dead:1,decor:5,def:5,defaultbackwardsemant:[12,13],defaultdict:0,defaultforwardsemant:12,defaultsemant:12,defin:12,definit:4,depend:2,descend:[4,5],determin:4,diagon:2,dict:[0,4],dictionari:5,differ:2,direct:[5,12],displai:[5,12],distinct:[0,2],div:5,div_call_semant:12,divis:12,doc:5,docstr:5,doe:[2,4],domain:[2,4,11],don:5,down:5,dure:5,each:[0,1,4,5],edg:5,either:5,element:[0,1,2,4],empti:[2,4],encount:2,enea:2,engin:[10,11],enough:2,enter:[0,1],enter_if:[0,1,2,3,4],enter_loop:[0,1,2,3,4],entranc:5,entri:[2,4],enumer:2,eq_call_semant:12,equal:[0,1,5,12],ether:1,evalu:[0,2,3,12],evaluate_liter:0,everi:[2,5],exact:2,exampl:[2,5],except:2,execut:12,exist:[2,5],exit:[0,1],exit_if:[0,1,2,3,4],exit_loop:[0,1,2,3,4],exp:3,expand:5,expandercleanup:5,expect:0,explicit:[0,5],expr:[2,5],express:[0,1,2,3,4,5,12],expressions_tool:[2,5],expressiontransform:[2,5],expressionvisitor:[2,5],extend:[2,5],fals:[2,3,5],field:5,fieldnam:5,filter:0,finalize_result:5,find:4,first:2,flag:4,flow:[5,6],foo:5,forget:2,form:2,format:2,forward:[5,6,12],forwardinterpret:6,forwardsemant:[6,12],found:5,from:[0,1,2,5],from_interval_domain:2,fromfunc:5,gener:[2,5],generic_visit:[2,5],get:[5,6],get_bound:2,get_interv:2,get_lb:2,get_node_result:6,get_ub:2,given:5,graph:[5,6],greater:12,greatest:[0,1],gt_call_semant:12,gte:5,gte_call_semant:12,has:[2,5],here:5,hill:2,hold:[0,1,2,4],html:5,http:5,hyper:3,ident:12,identifi:5,ids:5,idx:3,if_in:5,if_out:5,iff:2,implement:[0,2],impli:2,improv:2,in_call_semant:12,in_edg:5,in_nod:5,includ:[2,5],independ:12,index1:2,index2:2,index:[2,4,5,10,12],index_stmt_semant:12,indexstmt:[5,12],indic:2,inequ:12,inf:2,inform:2,ingo:5,initi:6,input:[2,3,5],input_call_semant:12,insid:2,instanc:0,instead:[2,5],int_call_semant:12,integ:2,integercdbm:2,intenum:[1,5],interest:2,interfac:[0,2],intern:2,interpret:[2,6,7,8,9],intersect:2,interv:2,interval_domain:2,interval_stor:2,intervaldomain:2,intervallattic:2,invalidformerror:2,invert:[2,5],is_bottom:[0,1,2],is_call_semant:12,is_top:[0,1,2,4],isnot:5,isnot_call_semant:12,item:[2,5],iter_child_expr:5,iter_field:5,its:[0,1,5],itself:5,join:[0,2,5],just:5,keep:5,kei:2,kind:[0,2,5],kindmixin:0,known:5,kwarg:[2,5],lambda:0,lattic:[1,2,3,4,11],law:5,least:[0,1],left:[0,1,2,5],less:[0,1,12],less_equ:0,lift:0,like:5,line:5,linear:[2,4],linear_form:2,linearform:2,list:[0,1,2,3,4,5,6,12],list_display_stmt_semant:12,listdisplai:5,listdisplaystmt:[5,12],listsemant:12,liter:[0,2,5,12],literal_evaluation_semant:12,literalevalu:[5,12],literalevaluationsemant:12,live:[0,6,11],liveness_analysi:7,liveness_domain:1,livenessanalysi:7,livenesslattic:1,livenessst:1,load:5,locat:5,lookup:5,loop:[0,1,5],loop_in:5,loop_out:5,lower:[0,1,2,5],lower_octagonal_constraint:2,lower_ub:2,lt_call_semant:12,lte:5,lte_call_semant:12,mai:[1,2,5],main:6,make_condition_not_fre:5,map:[0,1],matrix:2,meant:5,meet:[0,2],membership:12,method:[0,2,5,12],methodnam:4,mind:5,minu:[2,12],mismatch:12,mixin:[0,2],modif:5,modifi:[0,1,5,12],modul:10,more:2,morgan:5,mult:[2,5],mult_call_semant:12,multipl:[0,12],multipli:5,must:5,mutabl:0,name:[5,12],nan2inf:2,neg:[2,5],negat:[2,5,12],node:[5,6],nodes_backward:5,nodes_forward:5,nodevisitor:5,non:12,none:[2,5,6],nonetyp:5,not_call_semant:12,note:2,noteq:5,noteq_call_semant:12,notfreeconditiontransform:5,notin:5,notin_call_semant:12,number:5,numer:[0,11],numericalmixin:2,object:[0,2,3,5,6,12],occurr:5,octagon:2,octagon_domain:2,octagondomain:2,octagonlattic:2,old:5,one:2,onli:[2,5],oper:[0,2,5,12],operand:5,or_call_semant:12,order:[0,1,5],org:5,origin:5,other:[0,1,2,4],otherwis:[2,5],out:5,out_edg:5,out_nod:5,outer:4,outermost:5,outgo:5,output:[0,1],overrid:5,overwrit:5,packag:[10,11],page:10,paper:2,param:12,paramet:[0,1,2,5,6,12],part:[2,5],partial:[0,1],path:6,patricia:2,per:5,perform:0,place:5,plu:[2,12],point:0,pop:[0,4],posit:2,possibl:[2,4],predecessor:5,predefin:0,present:5,previous:[0,4],primari:5,print:12,print_call_semant:12,program:[0,1,4],programpoint:5,provid:[0,5],push:[0,4,5],python:5,rais:2,raise_lb:2,rather:5,recurs:[2,5],redefin:1,refer:5,relat:2,remov:5,render:6,repetit:12,replac:[0,2,3,5],repres:[0,1,2,6],represent:[2,4,5],reset:2,result:[0,5,6],revers:5,reverse_oper:5,rewrit:5,rewritenam:5,rid:5,right:[0,1,2,5],roberto:2,routin:5,row:2,run:[5,6],runner:[6,7,8,9],runtest:4,same:[2,5],satisfi:[0,1,2],scope:4,search:[4,10],second:2,see:2,self:5,semant:[6,10,11],sequenc:[4,5],set:[0,2,3,4,5,6],set_bound:2,set_empti:2,set_interv:2,set_lb:2,set_node_result:6,set_octagonal_constraint:2,set_ub:2,set_used_at:4,sever:2,show:2,sign1:2,sign2:2,simple_stmt:5,simplifi:5,sinc:2,singl:[2,5],singleton:5,singlevarlinearform:2,size:[2,5],slice:[5,12],slice_stmt_semant:12,slicestmt:[5,12],smallerequalconditiontransform:2,snake_cas:12,some:[0,1,4],someth:[0,1],sourc:[0,1,2,3,4,5,6,7,8,9,12,13],special:[2,5],special_express:[2,5],specifi:[4,5],stack:[4,11],stai:2,start:[4,5],state:[0,1,2,3,4,6,7,8,9,12,13],statement:[0,1,5,12,13],statu:1,step:5,stmt:[5,12,13],store:[1,2,4,5,11],str:[0,3,5,12],strong:2,strongly_clos:2,structur:2,sub:[2,5],sub_call_semant:12,subclass:[0,5],submodul:11,subpackag:11,subscript:5,substitut:[0,1],substitute_vari:0,subtract:12,success:2,successor:5,suo:4,support:0,switch_constraint:2,symmetr:2,syntax:5,system:2,take:5,target:5,term:2,test:[0,1,3],test_combin:4,test_usedliststartlattic:4,testcas:4,testusedliststartlattic:4,than:[0,1,5,12],thi:[0,2,4,5],through:4,tight:2,tightly_clos:2,to_interval_domain:2,top:[0,1,2,4],topmixin:0,trace:[0,6,11],traces_analysi:8,traces_domain:3,transform:[2,5],translat:2,travers:5,tree:[2,5,6],tryfin:5,tupl:[2,3,5],tvltrace:3,tvltracesanalysi:8,tvltracesst:3,two:[0,1,2],typ:5,type:[0,1,2,3,4,5,6],uadd_call_semant:12,unari:[2,5,12],unary_oper:12,unaryarithmeticoper:[2,5],unarybooleanoper:[2,5],unaryoper:[5,12],unclos:2,uncondit:5,underli:2,union:[2,5],unittest:4,updat:0,upper:[0,1,2,5],usag:[0,6,11,12],usage_analysi:9,usage_semant:13,usageanalysi:9,usagesemant:13,use:[2,5],used:[1,4,5],used_at:4,used_liststart:4,usedlattic:4,usedliststartlattic:4,usedstack:4,usedstor:4,useful:5,user:12,user_defined_call_semant:[12,13],userdefinedcallsemant:12,uses:4,usual:5,usub_call_semant:12,util:5,val:5,valu:[1,2,3,5],valueerror:2,var1:2,var2:2,var_sign:2,var_summand:2,variabl:[0,2,3,4,12],variable_access_semant:12,variableaccess:[5,12],variableaccesssemant:12,variableidentifi:[0,1,2,3,4,5],variad:5,variadicarithmeticoper:[2,5],variant:2,varieti:3,visit:[2,5],visit_:5,visit_binaryarithmeticoper:[2,5],visit_binarybooleanoper:[2,5],visit_binarycomparisonoper:[2,5],visit_input:2,visit_liter:[2,5],visit_nam:5,visit_tryfin:5,visit_unaryarithmeticoper:[2,5],visit_unarybooleanoper:[2,5],visit_variableidentifi:2,visit_variadicarithmeticoper:[2,5],visitor:[2,5],walk:5,want:5,were:5,whether:[0,1],which:[2,5],whole:2,widen:[0,1,6],wise:0,within:2,without:2,would:5,xor:[5,12],xor_call_semant:12,yield:5,you:5,your:5,yourself:5,yourtransform:5,zaffanella:2,zip:2},titles:["abstract_domains package","abstract_domains.liveness package","abstract_domains.numerical package","abstract_domains.traces package","abstract_domains.usage package","core package","engine package","engine.liveness package","engine.traces package","engine.usage package","Welcome to Lyra\u2019s documentation!","Lyra","semantics package","semantics.usage package"],titleterms:{"abstract":[0,1],abstract_domain:[0,1,2,3,4],core:5,document:10,domain:[0,1],engin:[6,7,8,9],indic:10,lattic:0,live:[1,7],lyra:[10,11],numer:2,packag:[0,1,2,3,4,5,6,7,8,9,12,13],semant:[12,13],stack:0,store:0,submodul:[0,1,2,3,4,5,6,7,8,9,12,13],subpackag:[0,6,12],tabl:10,trace:[3,8],usag:[4,9,13],variabl:1,welcom:10}})