// After: Added external dependencies
import lodash from 'lodash';
import moment from 'moment';
import validator from 'validator';

function calculateSum(numbers) {
    return lodash.sum(numbers);
}

function validateEmail(email) {
    return validator.isEmail(email);
}

function formatDate(date) {
    return moment(date).format('DD/MM/YYYY');
}

function processUsers(users) {
    return lodash.chain(users)
                 .filter('active')
                 .map(user => lodash.pick(user, ['name', 'email']))
                 .value();
}
