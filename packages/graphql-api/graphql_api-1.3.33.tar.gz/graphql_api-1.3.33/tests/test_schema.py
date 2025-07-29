# noinspection PyPep8Naming,DuplicatedCode
from graphql_api import GraphQLAPI, field, type


class TestGraphQLSchema:
    def test_decorators_no_schema(self):
        @type
        class ObjectNoSchema:
            @field
            def test_query_no_schema(self, a: int) -> int:
                pass

            @field(mutable=True)
            def test_mutation_no_schema(self, a: int) -> int:
                pass

        @type(abstract=True)
        class AbstractNoSchema:
            @field
            def test_abstract_query_no_schema(self, a: int) -> int:
                pass

            @field(mutable=True)
            def test_abstract_mutation_no_schema(self, a: int) -> int:
                pass

        @type(interface=True)
        class InterfaceNoSchema:
            @field
            def test_interface_query_no_schema(self, a: int) -> int:
                pass

            @field(mutable=True)
            def test_interface_mutation_no_schema(self, a: int) -> int:
                pass

        # noinspection PyUnresolvedReferences
        assert ObjectNoSchema._graphql
        assert ObjectNoSchema.test_query_no_schema._graphql
        assert ObjectNoSchema.test_mutation_no_schema._graphql

        # noinspection PyUnresolvedReferences
        assert AbstractNoSchema._graphql
        assert AbstractNoSchema.test_abstract_query_no_schema._graphql
        assert AbstractNoSchema.test_abstract_mutation_no_schema._graphql

        # noinspection PyUnresolvedReferences
        assert InterfaceNoSchema._graphql
        assert InterfaceNoSchema.test_interface_query_no_schema._graphql
        assert InterfaceNoSchema.test_interface_mutation_no_schema._graphql

    def test_decorators_schema(self):
        api_1 = GraphQLAPI()

        @api_1.type
        class ObjectSchema:
            @api_1.field
            def test_query_schema(self, a: int) -> int:
                pass

            @api_1.field(mutable=True)
            def test_mutation_schema(self, a: int) -> int:
                pass

        # noinspection PyUnresolvedReferences
        assert ObjectSchema._graphql
        assert ObjectSchema.test_query_schema._graphql
        assert ObjectSchema.test_mutation_schema._graphql

    def test_decorators_no_schema_meta(self):
        @type(meta={"test": "test"})
        class ObjectNoSchemaMeta:
            @field(meta={"test": "test"})
            def test_query_no_schema_meta(self, a: int) -> int:
                pass

            @field(meta={"test": "test"}, mutable=True)
            def test_mutation_no_schema_meta(self, a: int) -> int:
                pass

        # noinspection PyUnresolvedReferences
        assert ObjectNoSchemaMeta._graphql
        assert ObjectNoSchemaMeta.test_query_no_schema_meta._graphql
        assert ObjectNoSchemaMeta.test_mutation_no_schema_meta._graphql

    def test_decorators_schema_meta(self):
        api_1 = GraphQLAPI()

        @api_1.type(meta={"test1": "test2"}, is_root_type=True)
        class ObjectSchemaMeta:
            @api_1.field(meta={"test3": "test4"})
            def test_query_schema_meta(self, a: int) -> int:
                pass

            @api_1.field(meta={"test5": "test6"}, mutable=True)
            def test_mutation_schema_meta(self, a: int) -> int:
                pass

        # noinspection PyUnresolvedReferences
        assert ObjectSchemaMeta._graphql
        assert ObjectSchemaMeta.test_query_schema_meta._graphql
        assert ObjectSchemaMeta.test_mutation_schema_meta._graphql

        schema = api_1.build_schema()

        assert schema
