const { ApolloServer, gql } = require('apollo-server');
const { FunctionAPI, AppsAPI, UserInfoAPI } = require('./dataSources');

const typeDefs = gql`
    type User {
        id: String
        username: String
        name: String
        last_name: String
        first_name: String
        email: String
        institution: String
        source_id: String
        session: String
        saved_searches: String
        webhooks: [Webhook]
    }

    type WebhookType {
        id: String
        type: String
        template: String
    }

    type Webhook {
        id: String
        url: String
        topics: [String]
        type: WebhookType
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
        id: async (user, _args, { dataSources }) => {
            return dataSources.appsAPI.getUserInfo(user.username)
        },

        saved_searches: async (user, _args, { dataSources }) => {
            return dataSources.userInfoAPI.getSavedSearches(user.username);
        },

        session: async(user, _args, { dataSources }) => {
            return dataSources.userInfoAPI.getSession(user.username);
        },

        webhooks: async(user, _args, { dataSources }) => {
            return dataSources.appsAPI.getUserWebhooks(user.username);
        },
    },
};
    
const server = new ApolloServer({
    typeDefs,
    resolvers,
    dataSources: () => {
        return {
            functionAPI: new FunctionAPI(),
            appsAPI: new AppsAPI(),
            userInfoAPI: new UserInfoAPI(),
        };
    },
});

server.listen().then(({ url }) => {
    console.log(`🚀  Server ready at ${url}`);
});
