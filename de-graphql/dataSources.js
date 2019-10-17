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

    async getUserWebhooks(username) {
        const data = await this.get(`webhooks?user=${username}`);
        return data.webhooks;
    }

    async getAccessibleApps(username) {
        const data = await this.get(`apps?user=${username}`);
        return data.apps;
    }

    async getSystemIDs(username) {
        const data = await this.get(`bootstrap?user=${username}`);
        return data.system_ids;
    }

    async getWorkspace(username) {
        const data = await this.get(`workspaces?user=${username}`);
        const { 'user_id': _, ...newData } = data;
        return newData;
    }
}

class UserInfoAPI extends RESTDataSource {
    constructor() {
        super();
        this.baseURL = process.env.USER_INFO_URL;
    }

    async getSession(username) {
        return await this.get(`sessions/${username}@iplantcollaborative.org`);
    }

    async getSavedSearches(username) {
        return await this.get(`searches/${username}@iplantcollaborative.org`);
    }

    async getPreferences(username) {
        return await this.get(`preferences/${username}@iplantcollaborative.org`);
    }
}

module.exports = {
    FunctionAPI,
    AppsAPI,
    UserInfoAPI,
}