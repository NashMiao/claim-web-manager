new Vue({
    el: '#vue-app',
    data: function () {
        return {
            loginDialogVisible: true,
            loginForm: {
                identityPass: ''
            },
            settingForm: settingForm
        }
    },
    methods: {
        getIdentities: getIdentities,
        changeToFirstIdentity: changeToFirstIdentity,
        loginIdentityChange: loginIdentityChange,
        createIdentity: createIdentity,
        networkChange: networkChange,
        clearNewIdentityHexPrivateKey: clearNewIdentityHexPrivateKey,
        async sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        reloadLoginPage() {
            window.location.reload();
        },
        async handleLoginDialogClose(done) {
            await this.$confirm('Are you sure to close this dialog?', 'Warning', {
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancel',
                type: 'warning'
            }).then(_ => {
                window.location.reload();
            }).catch(_ => {
            });
        },
        async login() {
            if (this.loginForm.identityPass === '') {
                this.$message({
                    type: 'error',
                    message: 'Please input password',
                    duration: 3000
                });
                return
            }
            let unlock_url = Flask.url_for('unlock_identity');
            let redirect_url = '';
            try {
                let response = await axios.post(unlock_url, {
                    'ont_id': this.settingForm.ontIdSelected,
                    'pwd': this.loginForm.identityPass
                });
                redirect_url = response.data.redirect_url;
                this.$message({
                    type: 'success',
                    center: true,
                    message: response.data.result,
                    duration: 3000
                });
            } catch (error) {
                redirect_url = error.response.data.redirect_url;
                this.$message({
                    type: 'error',
                    center: true,
                    message: error.response.data.result,
                    duration: 3000
                });
            }
            await this.sleep(2000);
            this.loginForm.identityPass = '';
            window.location.replace(redirect_url);
        }
    },
    async created() {
        await this.getIdentities();
        await this.changeToFirstIdentity();
    }
});