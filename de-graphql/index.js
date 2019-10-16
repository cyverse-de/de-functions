const { ApolloServer, gql } = require('apollo-server');
const { RESTDataSource } = require('apollo-datasource-rest');

class FunctionAPI extends RESTDataSource {
    constructor() {
        super();
        this.baseURL = process.env.GATEWAY;
    }

    async getUserInfo(username) {
        var data =  await this.post(
            'function/get-user-info',
            {'username':username},
        )

        // Need to rename the id field to username
        data = JSON.parse(data);
        data.username = data.id
        delete data.id
        
        return data;
    }
}

const typeDefs = gql`
    type User {
        username: String
        name: String
        last_name: String
        full_name: String
        email: String
        institution: String
        source_id: String
    }

    type Query {
        user(username: String): User
    }
`;

const resolvers = {
    Query: {
        user: async (_source, { username }, { dataSources }) => {
            return dataSources.functionAPI.getUserInfo(username);
        },
    },
};
    
const server = new ApolloServer({
    typeDefs,
    resolvers,
    dataSources: () => {
        return {
            functionAPI: new FunctionAPI(),
        };
    },
});

server.listen().then(({ url }) => {
    console.log(`🚀  Server ready at ${url}`);
});
