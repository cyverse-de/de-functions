const { ApolloServer, gql } = require('apollo-server');
const { FunctionAPI, AppsAPI, UserInfoAPI } = require('./dataSources');

const typeDefs = gql`
    """A user of the Discovery Environment"""
    type User {
        """The unique identifier for the user. Should be a UUID."""
        id: String

        """The short username for the user. Does not include @iplantcollaborative.org"""
        username: String

        """The full name of the user, combining their first name and last name."""
        name: String

        """The last name of the user."""
        last_name: String

        """The first name of the user."""
        first_name: String

        """The contact email address for the user."""
        email: String

        """The university the user is associated with."""
        institution: String

        source_id: String

        """A JSON encoded string containing the layout settings."""
        session: String

        """A JSON encoded string containing the user's saved searches."""
        saved_searches: String

        """A JSON encoded string containing the user's preferences."""
        preferences: String

        """The user's workspace information."""
        workspace: Workspace

        """The user's system_id configuration."""
        system_ids: SystemIDs

        """The webhooks the user has configured."""
        webhooks: [Webhook]

        """The list of Apps that the user has access to."""
        accessible_apps: [App]
    }

    type Workspace {
        id: String
        root_category_id: String
        is_public: Boolean
        new_workspace: Boolean
    }

    type SystemIDs {
        de_system_id: String
        all_system_ids: [String]
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

    type AppRating {
        average: Float
        total: Float
        user: Int
        comment_id: Int
    }

    type AppPipelineEligibility {
        is_valid: Boolean
        reason: String
    }

    type App {
        id: String
        integration_date: String
        description: String
        deleted: Boolean
        is_favorite: Boolean
        integrator_name: String
        beta: Boolean
        permission: String
        can_favor: Boolean
        disabled: Boolean
        can_rate: Boolean
        name: String
        system_id: String
        is_public: Boolean
        edited_date: String
        step_count: Int
        can_run: Boolean
        integrator_email: String
        app_type: String
        wiki_url: String
        rating: AppRating
        pipeline_eligibility: AppPipelineEligibility

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

        session: async (user, _args, { dataSources }) => {
            return dataSources.userInfoAPI.getSession(user.username);
        },

        preferences: async (user, _args, { dataSources }) => {
            return dataSources.userInfoAPI.getPreferences(user.username);
        },

        webhooks: async (user, _args, { dataSources }) => {
            return dataSources.appsAPI.getUserWebhooks(user.username);
        },

        accessible_apps: async (user, _args, { dataSources }) => {
            return dataSources.appsAPI.getAccessibleApps(user.username);
        },

        workspace: async (user, _args, { dataSources }) => {
            return dataSources.appsAPI.getWorkspace(user.username);
        },

        system_ids: async (user, _args, { dataSources }) => {
            return dataSources.appsAPI.getSystemIDs(user.username);
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
