new Vue({
    el: '#vue-app',
    data: function () {
        return {
            chesiccTableVisible: chesiccTableVisible,
            chesiccClaim: chesiccClaim,
        }
    },
    methods: {
        reloadPotPage: reloadPotPage,
        getChesiccClaimInfo: getChesiccClaimInfo,
        async getOntId() {
            let ontId = await dApi.client.api.identity.getIdentity();
            console.log(ontId);
            let url = Flask.url_for('ontid');
            console.log(url);
        }
    },
    async created() {
        await dApi.client.registerClient({});
        await this.getOntId();
        await this.getChesiccClaimInfo();
    }
});
