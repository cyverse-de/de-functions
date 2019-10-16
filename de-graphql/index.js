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

class AppsAPI extends RESTDataSource {
    constructor() {
        super();
        this.baseURL = process.env.APPS_URL;
    }

    async getUserInfo(username) {
        const data = await this.get(`users/authenticated?user=${username}`);
        return data.id;
    }
}

const typeDefs = gql`
    type User {
        id: String
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

    User: {
        id: async(user, _args, { dataSources }) => {
            return dataSources.appsAPI.getUserInfo(user.username)
        }
    }
};
    
const server = new ApolloServer({
    typeDefs,
    resolvers,
    dataSources: () => {
        return {
            functionAPI: new FunctionAPI(),
            appsAPI: new AppsAPI(),
        };
    },
});

server.listen().then(({ url }) => {
    console.log(`🚀  Server ready at ${url}`);
});
